import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from matplotlib import pyplot as plt
from typing import Dict, Tuple

class SignaturePipeline:
    """
    Paso a paso:
      1.  Detecta la firma en dos fotos de INE  (método _extract_ine_signature)
      2.  Detecta la firma en otro documento    (método _extract_doc_signature)
      3.  Compara las firmas                   (método compare)
    """

    # ---------------------------  Init  --------------------------- #
    def __init__(
        self,
        firma_detector_model,               # YOLO/DETR entrenado para detectar firmas
        conf_ine: float = 0.5,                  # score mínimo del detector
        conf_doc: float = 0.5,                  # score mínimo del detector
        visualize: bool = True,                 # mostrar firmas comparadaas
        visualize_ine: bool = False,             # mostrar pasos intermedios
        visualize_doc: bool = False,             # mostrar pasos intermedios
        compare_threshold: float = 0.7             # score mínimo del comparación
    ):
        self.firma_detector_model = firma_detector_model
        self.conf_ine                 = conf_ine
        self.conf_doc                 = conf_doc
        self.visualize_ine       = visualize_ine
        self.visualize_doc       = visualize_doc
        self.visualize           = visualize
        self.compare_threshold     = compare_threshold

    #------------------- AUXILIAR: gris + uint8 ------------------- #
    @staticmethod
    def _to_gray_u8(img: np.ndarray) -> np.ndarray:
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
    def _detect_signature_on_single_ine_image(self, img_path: str) -> np.ndarray:
        """
        Devuelve el ROI de la firma en una foto de INE.
        Lanza RuntimeError si no hay EXACTAMENTE una firma detectada.
        """
        if not os.path.isfile(img_path):
            raise RuntimeError(f"El archivo no existe: {img_path}")

        img  = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1) Aislar credencial
        _, th   = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        dil     = cv2.dilate(th, np.ones((5, 5), np.uint8), iterations=2)
        cnts,_  = cv2.findContours(dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts:
            raise RuntimeError("No se encontró la credencial en la imagen.")

        x, y, w, h = cv2.boundingRect(max(cnts, key=cv2.contourArea))
        ine_crop   = img[y:y+h, x:x+w]

        # 2) Detectar firma con YOLO/DETR
        preds  = self.firma_detector_model.predict(ine_crop, conf=self.conf_ine)
        boxes  = preds[0].boxes
        if len(boxes) == 0:
            raise RuntimeError("No se detectó firma en Ine.")
        if len(boxes) > 1:
            raise RuntimeError("Se detectaron varias firmas en Ine.")

        x1, y1, x2, y2 = boxes.xyxy[0].cpu().numpy().astype(int)
        roi = ine_crop[y1:y2, x1:x2]

        # Visualización opcional
        if self.visualize_ine:

            plt.figure(figsize=(3,3)); plt.imshow(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
            plt.title(f"Firma detectada Ine\n{os.path.basename(img_path)}"); plt.axis("off")

        return roi


    def _extract_ine_signature(
        self,
        image_path:   str,
        image_2_path: str
    ) -> np.ndarray:
        """
        Intenta extraer la firma de `image_path`.
        Si falla, lo reintenta con `image_2_path`.
        Lanza error sólo si ninguno de los dos contiene una firma válida.
        """
        last_error = None

        for path in (image_path, image_2_path):
            try:
                return self._detect_signature_on_single_ine_image(path)
            except RuntimeError as err:
                last_error = err            # guarda el motivo por si hay que propagarlo
                # Sigue al siguiente path

        # Si salimos del bucle es que ambos intentos fallaron
        raise RuntimeError(
            f"No se detectó una firma válida en ninguno de los dos archivos:\n"
            f"  · {image_path}\n"
            f"  · {image_2_path}\n"
            f"Motivo del último intento: {last_error}"
        )

    # --------------- 2. Firma en documento genérico --------------- #
    def _extract_doc_signature(self, img_path: str) -> np.ndarray:
        """
        Ejemplo simple: recorta la franja inferior (20 %) suponiendo que ahí
        aparece la firma.  Sustituye esta lógica por tu propio detector YOLO
        o un heurístico diferente si lo necesitas.
        """
        if not os.path.isfile(img_path):
            raise RuntimeError(f"El archivo no existe: {img_path}")
        
        img  = cv2.imread(img_path)

        # 1) Detectar firma con YOLO/DETR
        preds  = self.firma_detector_model.predict(img_path, conf=self.conf_doc)
        boxes  = preds[0].boxes
        if len(boxes) == 0:
            raise RuntimeError("No se detectó firma en Documento.")
        if len(boxes) > 1:
            raise RuntimeError("Se detectaron varias firmas en Documento.")

        x1, y1, x2, y2 = boxes.xyxy[0].cpu().numpy().astype(int)
        roi = img[y1:y2, x1:x2]

        # Visualización opcional
        if self.visualize_doc:

            plt.figure(figsize=(3,3)); plt.imshow(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
            plt.title(f"Firma detectada Documento\n{os.path.basename(img_path)}"); plt.axis("off")

        return roi

    
    # --------------- 3. Comparación de firmas --------------- #
    def _compare_signatures(
        self,
        fir_ine_img: np.ndarray,
        fir_doc_img: np.ndarray) -> Tuple[float, bool]:
        """
        Compara dos imágenes de firma con SSIM.

        Returns
        -------
        score  : float   -- valor SSIM ∈ [0, 1]
        is_match : bool  -- True si score ≥ self.compare_threshold
        """

        target_size = (300, 300)

        # --- Normalizar tamaño ---
        ine = cv2.resize(fir_ine_img,  target_size)
        doc = cv2.resize(fir_doc_img,  target_size)

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
    def compare(
        self,
        ine_img_1_path: str,
        ine_img_2_path: str,
        doc_img_path:   str
    ) -> Dict[str, float]:
        """
        Orquesta todo el flujo y devuelve:
            {
                "score" : SSIM,
                "match" : True / False
            }
        """
        sig_ine = self._extract_ine_signature(ine_img_1_path, ine_img_2_path)
        sig_doc = self._extract_doc_signature(doc_img_path)

        score, is_match = self._compare_signatures(sig_ine, sig_doc)
        return {"score": score, "match": is_match}
