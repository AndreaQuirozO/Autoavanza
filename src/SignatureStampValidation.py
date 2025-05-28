from SignatureComparison import SignatureComparator

class SignatureStampValidator:
    """
    A class to validate the presence and consistency of signatures and stamps on documents
    (factura, INE, tarjeta de circulación) using a trained signature comparison model.

    Attributes:
        pipe (SignatureComparator): Signature comparison pipeline for processing and comparing images.
        ine_path (str): File path to the INE image/PDF.
        factura_path (str): File path to the factura image/PDF.
        tarjeta_path (str): File path to the tarjeta de circulación image/PDF.
    """
    
    def __init__(self, model_path, ine_path, factura_path, tarjeta_path):
        """
        Initializes the SignatureStampValidator with the required document paths and model configuration.

        Args:
            model_path (str): Path to the YOLO signature detection model.
            ine_path (str): Path to the INE document (PDF/image).
            factura_path (str): Path to the factura document (PDF/image).
            tarjeta_path (str): Path to the tarjeta de circulación document (PDF/image).
        """
        self.pipe = SignatureComparator(
                ruta_modelo = model_path,
                conf_ine  = 0.5,                  # score mínimo del detector
                conf_doc = 0.5,                  # score mínimo del detector
                visualize = False,                 # mostrar firmas comparadaas
                save_signature_ine = True,             # mostrar pasos intermedios
                save_signature_factura = True,             # mostrar pasos intermedios
                compare_threshold = 0.7             # score mínimo del comparación    
            ) 
        self.ine_path = ine_path
        self.factura_path = factura_path
        self.tarjeta_path = tarjeta_path


    # Factura 8.
    def validar_presencia_sello_y_firma_factura(self):
        """
        Placeholder for manual validation of stamp and signature on the factura.

        Returns:
            str: Confirmation message assuming presence is validated manually.
        """
        # Valdiación manual mostrando factura
        # False: 'Se solicita sello y firma'
        return False, 'Se requiere de intervención humana para validar sello y firma en factura'
    
    # Factura 10.
    def validar_firma_factura_reverso(self):
        """
        Validates that the factura has a signature on the reverse side.

        Returns:
            tuple:
                - bool: True if signature is present, False otherwise.
                - str: Message indicating validation result.
        """
        factura_jpg_path = self.pipe.make_jpg(self.factura_path)
        
        roi, path_mess = self.pipe._extract_factura_signature(factura_jpg_path)
        
        if roi is not False:
            return True, 'Firma detectada en Reverso de Factura'
        else:
            if path_mess == "No se detectó firma en Reverso de Factura":
                return False, 'Se solicita endosar a favor de NMP ya que no se encontró firma en Reverso de Factura'
            return False, path_mess

    # INE 4.
    def validar_firma_ine_factura(self):       
        """
        Compares the signature from the INE with the one on the factura to verify identity.

        Returns:
            tuple:
                - bool: True if signatures match, False otherwise.
                - str: Message indicating validation result.
                - str or None: Path to saved INE signature image if available.
                - str or None: Path to saved factura signature image if available.
        """
        ine_jpg_path = self.pipe.make_jpg(self.ine_path)
        factura_jpg_path = self.pipe.make_jpg(self.factura_path)

        result, ine_save_path, factura_save_path = self.pipe.compare_ine_factura(ine_jpg_path, factura_jpg_path)

        if result is not False:
            if result['match'] == True:
                return True, 'Firma de INE coincide con Reverso de Factura', ine_save_path, factura_save_path
            if result['match'] == False:
                return False, 'Se requiere que el solicitante vuelva a firmar lo más parecido posible ya que no coincide firma en INE y Reverso de Factura', ine_save_path, factura_save_path
        else:
            if ine_save_path is not None:
                return False, 'No se encontró firma en Tarjeta de Circulación', ine_save_path, None
            elif factura_save_path is not None:
                return False, 'No se encontró firma en INE', None, factura_save_path
            else:
                return False, 'No se encontró firma en INE ni Tarjeta de Circulación', None, None
    
    
    # Tarjeta 4.
    def validar_firma_ine_tarjeta(self):
        """
        Compares the signature from the INE with the one on the tarjeta de circulación.

        Returns:
            tuple:
                - bool: True if signatures match, False otherwise.
                - str: Message indicating validation result.
                - str or None: Path to saved signature image (INE or tarjeta) if available.
                - str or None: Second image path if available (only when validation fails).
        """
        ine_jpg_path = self.pipe.make_jpg(self.ine_path)
        tarjeta_jpg_path = self.pipe.make_jpg(self.tarjeta_path)

        result, ine_save_path, tarjeta_save_path = self.pipe.compare_ine_tarjeta(ine_jpg_path, tarjeta_jpg_path)

        if result is not False:
            if result['match'] == True:
                return True, 'Firma de INE coincide con Tarjeta de Circulación', ine_save_path, tarjeta_save_path
            if result['match'] == False:
                return False, 'Se solicita corrección - en 24hrs. Se rechaza por discrepancia en firma de INE y Tarjeta de Circulación', ine_save_path, tarjeta_save_path
        else:
            if ine_save_path is not None:
                return False, 'No se encontró firma en Tarjeta de Circulación', ine_save_path, None
            elif tarjeta_save_path is not None:
                return False, 'No se encontró firma en INE', None, tarjeta_save_path
            else:
                return False, 'No se encontró firma en INE ni Tarjeta de Circulación', None, None
    

    def signature_stamp_validator_pipeline(self):
        """
        Runs the entire signature and stamp validation pipeline.

        Returns:
            dict: Dictionary containing validation results for each document.
        """
        validacion_sello_firma_bool, validacion_sello_firma_message = self.validar_presencia_sello_y_firma_factura()
        validacion_firma_factura_bool, validacion_firma_factura_message = self.validar_firma_factura_reverso()
        validacion_firma_ine_factura_bool, validacion_firma_ine_factura_message, validacion_firma_ine_factura_ine_save_path, validacion_firma_ine_factura_factura_save_path = self.validar_firma_ine_factura()
        validacion_firma_ine_tarjeta_bool, validacion_firma_ine_tarjeta_message, validacion_firma_ine_tarjeta_ine_save_path, validacion_firma_ine_tarjeta_tarjeta_save_path = self.validar_firma_ine_tarjeta()

        results_bool = {
            "validacion_sello_firma": validacion_sello_firma_bool,
            "validacion_firma_factura": validacion_firma_factura_bool,
            "validacion_firma_ine_factura": validacion_firma_ine_factura_bool,
            "validacion_firma_ine_tarjeta": validacion_firma_ine_tarjeta_bool
        }

        results_message = {
            "validacion_sello_firma": validacion_sello_firma_message,
            "validacion_firma_factura": validacion_firma_factura_message,
            "validacion_firma_ine_factura": validacion_firma_ine_factura_message,
            "validacion_firma_ine_tarjeta": validacion_firma_ine_tarjeta_message
        }

        results_path = {
            "validacion_firma_ine_factura_ine_path": validacion_firma_ine_factura_ine_save_path, 
            "validacion_firma_ine_factura_factura_path": validacion_firma_ine_factura_factura_save_path,
            "validacion_firma_ine_tarjeta_ine_path": validacion_firma_ine_tarjeta_ine_save_path,
            "validacion_firma_ine_tarjeta_tarjeta_path": validacion_firma_ine_tarjeta_tarjeta_save_path
        }
        
        return results_bool, results_message, results_path