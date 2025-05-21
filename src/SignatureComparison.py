import os
import cv2
import fitz  # PyMuPDF
import numpy as np
from skimage.metrics import structural_similarity as ssim
from matplotlib import pyplot as plt
from typing import Dict, Tuple
from ultralytics import YOLO
from Staging import Staging

class SignatureComparator:
    """
    Pipeline for detecting and comparing signatures in documents.

    This pipeline performs the following steps:
      1. Detects the signature in an INE (ID) image.
      2. Detects the signature in an invoice/document image.
      3. Compares both signatures using the Structural Similarity Index (SSIM).

    Attributes
    ----------
    firma_detector_model : YOLO
        Pre-trained YOLO model for signature detection.
    conf_ine : float
        Minimum confidence threshold for detection in INE.
    conf_doc : float
        Minimum confidence threshold for detection in invoice/document.
    visualize : bool
        If True, displays visualizations of the extracted signatures and comparison.
    save_signature_ine : bool
        If True, saves the cropped signature image from INE.
    save_signature_factura : bool
        If True, saves the cropped signature image from the document.
    compare_threshold : float
        Minimum SSIM similarity score to consider a match.
    staging_signatures : Staging
        Utility class for managing temporary file paths.
    staging_signatues_path : str
        Path where extracted signature images are temporarily saved.
    """

    # ---------------------------  Init  --------------------------- #
    def __init__(
        self,
        ruta_modelo,              # YOLO/DETR entrenado para detectar firmas
        conf_ine: float = 0.5,                  # score mínimo del detector
        conf_doc: float = 0.5,                  # score mínimo del detector
        visualize: bool = True,                 # mostrar firmas comparadaas
        save_signature_ine: bool = False,             # mostrar pasos intermedios
        save_signature_factura: bool = False,             # mostrar pasos intermedios
        compare_threshold: float = 0.7             # score mínimo del comparación
    ):
        self.firma_detector_model = YOLO(ruta_modelo)
        self.conf_ine                 = conf_ine
        self.conf_doc                 = conf_doc
        self.save_signature_ine       = save_signature_ine
        self.save_signature_factura       = save_signature_factura
        self.visualize           = visualize
        self.compare_threshold     = compare_threshold
        self.staging_signatures = Staging("signatures")
        self.staging_signatues_path = self.staging_signatures.run()

    def make_jpg(self, input_path: str) -> str:
        """
        Converts the first page of a PDF to a JPG image.

        Parameters
        ----------
        input_path : str
            Path to the PDF file.

        Returns
        -------
        ruta_jpg : str
            Path to the generated JPG file.
        """

        nombre_base = input_path.split('/')[-1].split('.')[0] + '.jpg'
        ruta_jpg = os.path.join(self.staging_signatues_path, nombre_base)

        doc = fitz.open(input_path)
        pix = doc[0].get_pixmap(dpi=200)
        pix.save(ruta_jpg)

        return ruta_jpg

    def delete_jpg(self, ruta_jpg: str) -> None:
        """
        Deletes a temporary JPG file.

        Parameters
        ----------
        ruta_jpg : str
            Path to the JPG file to delete.
        """

        if os.path.isfile(ruta_jpg):
            os.remove(ruta_jpg)

    #------------------- AUXILIAR: gris + uint8 ------------------- #
    @staticmethod
    def _to_gray_u8(img: np.ndarray) -> np.ndarray:
        """
        Converts an image to grayscale in uint8 format.

        Parameters
        ----------
        img : np.ndarray
            Image in color (BGR or RGB) or float.

        Returns
        -------
        np.ndarray
            Grayscale image in uint8 format.
        """

        """
        - Convierte BGR/RGB a escala de grises (1 canal)
        - Garantiza dtype uint8 (0-255)
        """
        # Si viene con 3 canales ⇒ BGR → GRAY
        if len(img.shape) == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Si está en float [0,1] o [0,255] ⇒ re-escala y castea
        if img.dtype != np.uint8:
            img = np.clip(img * 255, 0, 255).astype(np.uint8)

        return img

    # -------------------- 1. Firma en la INE ---------------------- #
    def _extract_ine_signature(self, img_path: str) -> Tuple[np.ndarray, str]:
        """
        Detects and crops the signature from an INE image.

        Parameters
        ----------
        img_path : str
            Path to the INE image.

        Returns
        -------
        Tuple[np.ndarray, str]
            - Cropped signature region as a NumPy array.
            - Path where the signature image was saved (only if save_signature_ine is True).

        Raises
        ------
        RuntimeError
            If exactly one signature is not detected.
        """


        if not os.path.isfile(img_path):
            return False, f"El archivo no existe: {img_path}"

        img  = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1) Aislar credencial
        _, th   = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        dil     = cv2.dilate(th, np.ones((5, 5), np.uint8), iterations=2)
        cnts,_  = cv2.findContours(dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts:
            return False, "No se encontró la credencial en la imagen"

        x, y, w, h = cv2.boundingRect(max(cnts, key=cv2.contourArea))
        ine_crop   = img[y:y+h, x:x+w]

        # 2) Detectar firma con YOLO/DETR
        preds  = self.firma_detector_model.predict(ine_crop, conf=self.conf_ine, verbose=False)
        boxes  = preds[0].boxes
        if len(boxes) == 0:
            return False, "No se detectó firma en INE"
        if len(boxes) > 1:
            return False, "Se detectaron varias firmas en INE"

        x1, y1, x2, y2 = boxes.xyxy[0].cpu().numpy().astype(int)
        roi = ine_crop[y1:y2, x1:x2]

        # Visualización opcional
        if self.save_signature_ine:
            roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

            # Save the image in the staging folder
            base_name = os.path.splitext(os.path.basename(img_path))[0]
            save_path = os.path.join(self.staging_signatues_path, f"firma_ine.jpg")
            cv2.imwrite(save_path, cv2.cvtColor(roi_rgb, cv2.COLOR_RGB2BGR))

        return roi, save_path


    # --------------- 2. Firma en documento genérico --------------- #
    def _extract_factura_signature(self, img_path: str) -> Tuple[np.ndarray, str]:
        """
        Extracts the signature from a document (invoice) using YOLO.

        Parameters
        ----------
        img_path : str
            Path to the document image.

        Returns
        -------
        Tuple[np.ndarray, str]
            - Cropped signature region as a NumPy array.
            - Path where the signature image was saved (only if save_signature_factura is True).

        Raises
        ------
        RuntimeError
            If exactly one signature is not detected.
        """


        if not os.path.isfile(img_path):
            return False, f"El archivo no existe: {img_path}"
        
        img  = cv2.imread(img_path)

        # 1) Detectar firma con YOLO/DETR
        preds  = self.firma_detector_model.predict(img_path, conf=self.conf_doc, verbose=False)
        boxes  = preds[0].boxes
        if len(boxes) == 0:
            return False, "No se detectó firma en Reverso de Factura"
        if len(boxes) > 1:
            return False, "Se detectaron varias firmas en Reverso de Factura"

        x1, y1, x2, y2 = boxes.xyxy[0].cpu().numpy().astype(int)
        roi = img[y1:y2, x1:x2]

        # Visualización opcional
        if self.save_signature_factura:
            roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

            # Save the image in the staging folder
            base_name = os.path.splitext(os.path.basename(img_path))[0]
            save_path = os.path.join(self.staging_signatues_path, f"firma_factura.jpg")
            cv2.imwrite(save_path, cv2.cvtColor(roi_rgb, cv2.COLOR_RGB2BGR))

        return roi, save_path
    
    # -------------------- 3. Firma en la INE ---------------------- #
    def _extract_tarjeta_signature(self, img_path: str) -> Tuple[np.ndarray, str]:
        """
        Detects and crops the signature from an INE image.

        Parameters
        ----------
        img_path : str
            Path to the INE image.

        Returns
        -------
        Tuple[np.ndarray, str]
            - Cropped signature region as a NumPy array.
            - Path where the signature image was saved (only if save_signature_ine is True).

        Raises
        ------
        RuntimeError
            If exactly one signature is not detected.
        """


        if not os.path.isfile(img_path):
            return False, f"El archivo no existe: {img_path}"

        img  = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1) Aislar credencial
        _, th   = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        dil     = cv2.dilate(th, np.ones((5, 5), np.uint8), iterations=2)
        cnts,_  = cv2.findContours(dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts:
            return False, "No se encontró la credencial en la imagen"

        x, y, w, h = cv2.boundingRect(max(cnts, key=cv2.contourArea))
        ine_crop   = img[y:y+h, x:x+w]

        # 2) Detectar firma con YOLO/DETR
        preds  = self.firma_detector_model.predict(ine_crop, conf=self.conf_ine, verbose=False)
        boxes  = preds[0].boxes
        if len(boxes) == 0:
            return False, "No se detectó firma en Tarjeta de Circulación"
        if len(boxes) > 1:
            return False, "Se detectaron varias firmas en Tarjeta de Circulación"

        x1, y1, x2, y2 = boxes.xyxy[0].cpu().numpy().astype(int)
        roi = ine_crop[y1:y2, x1:x2]

        # Visualización opcional
        if self.save_signature_ine:
            roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

            # Save the image in the staging folder
            base_name = os.path.splitext(os.path.basename(img_path))[0]
            save_path = os.path.join(self.staging_signatues_path, f"firma_tarjeta.jpg")
            cv2.imwrite(save_path, cv2.cvtColor(roi_rgb, cv2.COLOR_RGB2BGR))

        return roi, save_path

    
    # --------------- 4. Comparación de firmas --------------- #
    def _compare_signatures(
        self,
        fir_1_img: np.ndarray,
        fir_2_img: np.ndarray
    ) -> Tuple[float, bool]:
        """
        Compares two signatures using SSIM.

        Parameters
        ----------
        fir_ine_img : np.ndarray
            Signature image from the INE.
        fir_doc_img : np.ndarray
            Signature image from the document.

        Returns
        -------
        Tuple[float, bool]
            - SSIM score between 0 and 1.
            - True if the score is above the comparison threshold.
        """

        target_size = (300, 300)

        # --- Normalizar tamaño ---
        ine = cv2.resize(fir_1_img,  target_size)
        doc = cv2.resize(fir_2_img,  target_size)

        # --- Garantizar GRIS + uint8 ---
        ine = self._to_gray_u8(ine)
        doc = self._to_gray_u8(doc)

        # --- Binarización adaptativa ---
        ine_bin = cv2.adaptiveThreshold(
            ine, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
            11, 2
        )
        doc_bin = cv2.adaptiveThreshold(
            doc, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
            11, 2
        )

        # --- SSIM ---
        score = ssim(ine, doc)
        is_match = score >= self.compare_threshold


        if self.visualize:
            fig, axs = plt.subplots(2, 2, figsize=(8, 8))
            axs[0, 0].imshow(ine, cmap="gray"); axs[0, 0].set_title("INE"); axs[0, 0].axis("off")
            axs[0, 1].imshow(doc, cmap="gray"); axs[0, 1].set_title("DOC"); axs[0, 1].axis("off")
            axs[1, 0].imshow(ine_bin, cmap="gray"); axs[1, 0].set_title("INE bin");  axs[1, 0].axis("off")
            axs[1, 1].imshow(doc_bin, cmap="gray"); axs[1, 1].set_title("DOC bin");  axs[1, 1].axis("off")
            plt.suptitle(f"SSIM = {score:.3f}", fontsize=14)
            plt.tight_layout(); plt.show()

        return score, is_match

    # -------------------- 4. Comparación final -------------------- #
    def compare_ine_factura(self, ine_img_path: str, doc_img_path: str) -> Tuple[Dict[str, float], str, str]:
        """
        Runs the entire pipeline to detect and compare signatures.

        Parameters
        ----------
        ine_img_path : str
            Path to the INE image.
        doc_img_path : str
            Path to the document image.

        Returns
        -------
        Tuple[Dict[str, float], str, str]
            - Dictionary with the SSIM score and match result:
                {
                    "score": float,
                    "match": bool
                }
            - Path to the saved INE signature image (if saving is enabled).
            - Path to the saved document signature image (if saving is enabled).
        """


        sig_ine, ine_save_path = self._extract_ine_signature(ine_img_path)
        sig_doc, factura_save_path = self._extract_factura_signature(doc_img_path)

        if sig_ine is not False and sig_doc is not False:
            score, is_match = self._compare_signatures(sig_ine, sig_doc)
            return {"score": score, "match": is_match}, ine_save_path, factura_save_path
        else:
            if sig_ine is False and sig_doc is False:
                return False, None, None
            elif sig_ine is False:
                return False, None, factura_save_path
            elif sig_doc is False:
                return False, ine_save_path, None



    def compare_ine_tarjeta(self, ine_img_path: str, doc_img_path: str) -> Tuple[Dict[str, float], str, str]:
        """
        Runs the entire pipeline to detect and compare signatures.

        Parameters
        ----------
        ine_img_path : str
            Path to the INE image.
        doc_img_path : str
            Path to the document image.

        Returns
        -------
        Tuple[Dict[str, float], str, str]
            - Dictionary with the SSIM score and match result:
                {
                    "score": float,
                    "match": bool
                }
            - Path to the saved INE signature image (if saving is enabled).
            - Path to the saved document signature image (if saving is enabled).
        """


        sig_ine, ine_save_path = self._extract_ine_signature(ine_img_path)
        sig_tarjeta, tarjeta_save_path = self._extract_tarjeta_signature(doc_img_path)

        if sig_ine is not False and sig_tarjeta is not False:
            score, is_match = self._compare_signatures(sig_ine, sig_tarjeta)
            return {"score": score, "match": is_match}, ine_save_path, tarjeta_save_path
        else:
            if sig_ine is False and sig_tarjeta is False:
                return False, None, None
            elif sig_ine is False:
                return False, None, tarjeta_save_path
            elif sig_tarjeta is False:
                return False, ine_save_path, None