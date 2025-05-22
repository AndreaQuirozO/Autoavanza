import re
from dateutil import parser
from datetime import datetime
from dateutil.relativedelta import relativedelta

class DataValidator:
    """
    A class to validate various fields and documents related to vehicle ownership
    and registration, including invoices, SAT data, ID, and vehicle registration card.

    Attributes:
        datos_factura (dict): Invoice data.
        datos_factura_SAT (dict): SAT invoice data.
        datos_factura_reverso (dict): Reverse invoice data.
        datos_ine (dict): Voter ID data.
        datos_tarjeta (dict): Vehicle registration card data.
    """

    def __init__(self, datos_factura, datos_factura_SAT, datos_factura_reverso, datos_ine, datos_tarjeta):
        """
        Initialize the DataValidator with relevant datasets.

        Args:
            datos_factura (dict): Invoice data.
            datos_factura_SAT (dict): SAT invoice data.
            datos_factura_reverso (dict): Reverse invoice data.
            datos_ine (dict): Voter ID data.
            datos_tarjeta (dict): Vehicle registration card data.
        """

        self.datos_factura = datos_factura
        self.datos_factura_SAT = datos_factura_SAT
        self.datos_factura_reverso = datos_factura_reverso
        self.datos_ine = datos_ine
        self.datos_tarjeta = datos_tarjeta

    @staticmethod
    def convertir_a_datetime(fecha):
        """
        Convert a string date to a datetime object, if possible.

        Args:
            fecha (str): Date string to convert.

        Returns:
            datetime or None: Parsed datetime object or None if parsing fails.
        """
        try:
            # Attempt to parse the date automatically
            return parser.parse(fecha)
        except (ValueError, TypeError):
            # If parsing fails, return None or handle the error as needed
            return None


    def normalizar_nombre(self, nombre):
        """
        Normalize a name string by uppercasing, removing punctuation,
        splitting into words, and sorting them alphabetically.

        Args:
            nombre (str): Name string to normalize.

        Returns:
            list: Sorted list of normalized words.
        """
        nombre = nombre.upper()
        nombre = re.sub(r'[^\w\s]', '', nombre)  # remove punctuation
        palabras = nombre.split()
        return sorted(palabras)
    
    @staticmethod
    def son_fechas_equivalentes(fecha_str1, fecha_str2):
        """
        Determine if two date strings can be considered equivalent,
        accounting for ambiguous day/month order.

        Args:
            fecha_str1 (str): First date string.
            fecha_str2 (str): Second date string.

        Returns:
            bool: True if dates are equivalent, False otherwise.
        """
        try:
            # Try parsing the first date in both ways
            f1_dayfirst = parser.parse(fecha_str1, dayfirst=True)
            f1_monthfirst = parser.parse(fecha_str1, dayfirst=False)
            
            # Same for the second date
            f2_dayfirst = parser.parse(fecha_str2, dayfirst=True)
            f2_monthfirst = parser.parse(fecha_str2, dayfirst=False)
            
            # Compare only the date part (ignoring time)
            fechas1 = {f1_dayfirst.date(), f1_monthfirst.date()}
            fechas2 = {f2_dayfirst.date(), f2_monthfirst.date()}
            
            # If any interpretation of fecha_str1 matches any interpretation of fecha_str2, consider them equivalent
            return not fechas1.isdisjoint(fechas2)
        except Exception as e:
            print("Error parsing dates:", e)
            return False
        
    @staticmethod
    def extract_integers(text):
        """
        Extract all integers from a given text string.

        Args:
            text (str): Text to extract integers from.

        Returns:
            list[int]: List of integers found in the text.
        """
        return list(map(int, re.findall(r'\d+', text)))
    

    # Factura 1.
    def validar_nombre_solicitante(self):
        """
        Validate that the applicant's name matches across invoice, reverse invoice,
        voter ID, and vehicle registration card.

        Returns:
            bool: True if names match, False otherwise.
            str: Validation message indicating match or discrepancy.
        """
        nombre_solicitante_factura = self.normalizar_nombre(self.datos_factura['Nombre del solicitante'])
        nombre_solicitante_factura_reverso = self.normalizar_nombre(self.datos_factura_reverso['Nombre del nuevo dueño'])
        nombre_solicitante_ine = self.normalizar_nombre(self.datos_ine['Nombre del solicitante'])
        nombre_solicitante_tarjeta_circ = self.normalizar_nombre(self.datos_tarjeta['Nombre del solicitante'])
        
        if nombre_solicitante_factura == nombre_solicitante_ine or nombre_solicitante_ine == nombre_solicitante_factura_reverso: #agregar condicion firma primer dueño
            if nombre_solicitante_ine == nombre_solicitante_tarjeta_circ:
                return True, 'Nombre del solicitante coincide con Factura, INE y Tarjeta de Circulación'
            else:
                return False, 'Sin coincidencia en nombre del solicitante entre Factura, INE y Tarjeta de Circulación'
        else:
            return False, 'Trámite rechazado por discrepancia en nombre del solicitante'
        
    
    # Factura 2.
    def validar_niv(self):
        """
        Validate that the Vehicle Identification Number (NIV) matches
        between the invoice and vehicle registration card.

        Returns:
            bool: True if names match, False otherwise.
            str: Validation message indicating match or discrepancy.
        """
        if self.datos_factura['NIV'] == self.datos_tarjeta['NIV']:
            return True, 'NIV coincide en Factura con Tarjeta de Circulación'
        else:
            return False, 'Trámite rechazado por discrepancia en NIV' 

    # Factura 3.
    def validar_datos_vehiculo(self):
        """
        Validate vehicle details such as brand, model, and year
        between invoice and vehicle registration card.

        Returns:
            bool: True if names match, False otherwise.
            dict or str: Dictionary of discrepancies or confirmation message.
        """
        discrepancias = {}

        campos = {
            "Marca": "Discrepancia en marca",
            "Modelo": "Discrepancia en modelo",
            "Año": "Discrepancia en año",
            # "Versión": "Discrepancia en versión"  #Se usa version?
        }

        for campo, mensaje in campos.items():
            if self.datos_factura.get(campo) != self.datos_tarjeta.get(campo):
                discrepancias[campo] = f"{mensaje}: {self.datos_factura.get(campo)} es distinto a {self.datos_tarjeta.get(campo)}"

        if discrepancias:
            return False, {"Estado": "Se solicita ajuste en factura", "detalles": discrepancias}
        return True, {"Estado": "Datos de vehículo coinciden en Factura y Tarjeta de Circulación"}

    # No entiendo bien que se compara aquí
    # Factura 5.
    def validar_RFC(self):
        """
        Validate the RFC (Federal Taxpayer Registry) field.
        (Implementation detail not provided.)

        Returns:
            bool: True if names match, False otherwise.
            str: Placeholder validation message.
        """
        if self.datos_factura['RFC Receptor'] == self.datos_factura_SAT['RFC Receptor']:
            return True, 'RFC coincide'
        else:
            return False, 'RFC receptor no coincide en la Factura y el SAT'

    # Factura 6.
    def validar_es_primera_emision(self):
        """
        Check if the invoice corresponds to the first issuance.

        Returns:
            bool: True if names match, False otherwise.
            str: Message indicating if it's the first issuance or not.
        """
        texto = self.datos_factura['Leyenda primera emisión'].lower() 
        frases_clave = [
            "primera impresión",
            "primera en su orden",
            "primera emisión",
            "primera expedición", 
            "primera"
        ]
        words = any(frase in texto for frase in frases_clave)

        if words:
            return True, "Es la primera emisión"
        else:
            return False, "No es la primera emisión. Solicitar facturas anteriores"
        
    # Factura 7.# Factura 7. 
    def validar_datos_SAT(self):
        """
        Validate consistency between invoice data and SAT data.

        Returns:
            bool: True if names match, False otherwise.
            bool or str: True if all checks pass, otherwise a rejection message.
        """
        # Normalize names
        nombre_solicitante_factura = self.normalizar_nombre(self.datos_factura['Nombre del solicitante'])
        nombre_solicitante_factura_SAT = self.normalizar_nombre(self.datos_factura_SAT['Nombre Receptor'])
        nombre_emisor_factura = self.normalizar_nombre(self.datos_factura['Nombre Emisor'])
        nombre_emisor_factura_SAT = self.normalizar_nombre(self.datos_factura_SAT['Nombre Emisor'])
        
        # Dates as original strings (needed for ambiguous date comparison)
        fecha_certificacion_factura_str = self.datos_factura['Fecha Certificación']
        fecha_certificacion_SAT_str = self.datos_factura_SAT['Fecha Certificación']
        fecha_expedicion_factura_str = self.datos_factura['Fecha Expedición']
        fecha_expedicion_SAT_str = self.datos_factura_SAT['Fecha Expedición']
        
        
        if nombre_solicitante_factura == nombre_solicitante_factura_SAT:
            if nombre_emisor_factura == nombre_emisor_factura_SAT:
                if self.datos_factura['RFC Receptor'] == self.datos_factura_SAT['RFC Receptor']:
                    if self.datos_factura['RFC Emisor'] == self.datos_factura_SAT['RFC Emisor']:
                        # Compare certification dates using our ambiguous date function
                        if self.son_fechas_equivalentes(fecha_certificacion_factura_str, fecha_certificacion_SAT_str):
                            # Compare expedition dates likewise
                            if self.son_fechas_equivalentes(fecha_expedicion_factura_str, fecha_expedicion_SAT_str):
                                if self.datos_factura['Folio Fiscal'] == self.datos_factura_SAT['Folio Fiscal']:
                                    return True, 'Trámite aceptado, datos de Factura coinciden con datos del SAT'
                                else:
                                    return False, 'Trámite rechazado por discrepancia en folio fiscal'
                            else:
                                return False, 'Trámite rechazado por discrepancia en fecha de expedición'
                        else:
                            return False, 'Trámite rechazado por discrepancia en fecha de certificación'
                    else:
                        return False, 'Trámite rechazado por discrepancia en RFC emisor'
                else:
                    return False, 'Trámite rechazado por discrepancia en RFC receptor'
            else:
                return False, 'Trámite rechazado por discrepancia en nombre del emisor'
        else:
            return False, 'Trámite rechazado por discrepancia en el nombre del solicitante en la Factura y el SAT'
        
        
    # Factura 9.
    def validar_no_motor(self):
        """
        Validate that the engine number matches between invoice and vehicle registration card.

        Returns:
            bool: True if names match, False otherwise.
            str: Validation message indicating match or discrepancy.
        """
        if self.datos_factura['Número de motor'] == self.datos_tarjeta['Número de motor']:
            return True, 'Número de motor coincide en Factura y Tarjeta de Circulación'
        else:
            if self.datos_factura['Número de motor'][-len(self.datos_tarjeta['Número de motor']):] == self.datos_tarjeta['Número de motor']:
                return True, 'Número de motor coincide en Factura y Tarjeta de Circulación'
            return False, 'No hay coincidencia en número de motor'

    # Factura 11.
    def validar_endoso(self):
        """
        Validate the endorsement by comparing applicant names in invoice,
        reverse invoice, and voter ID.

        Returns:
            bool: True if names match, False otherwise.
            str: Message indicating endorsement status.
        """
        nombre_solicitante_factura = self.normalizar_nombre(self.datos_factura['Nombre del solicitante'])
        nombre_solicitante_factura_reverso = self.normalizar_nombre(self.datos_factura_reverso['Nombre del nuevo dueño'])
        nombre_solicitante_ine = self.normalizar_nombre(self.datos_ine['Nombre del solicitante'])

        if nombre_solicitante_factura == nombre_solicitante_ine:
            return True, 'No hay necesidad de endoso'
        elif nombre_solicitante_factura_reverso == nombre_solicitante_ine:
            return True, 'Endoso correcto'
        else:
            return False, 'Se solicita endoso al cliente'
        
    # INE 2.
    def validar_vigencia_INE(self):
        """
        Validate the issuance date to ensure it is not in the future
        and not older than one year from today.

        Returns:
            bool: True if names match, False otherwise.
            str: Validation message about date of issuance.
        """
        if self.datos_ine['Vigente']:
            return True, 'INE vigente'
        else:
            return False, 'Se solicita INE vigente, o cita del INE y pasaporte mexicano'
        
    

    # Tarjeta 2.
    def validar_vigencia_tarjeta(self):
        """
        Validates the expiration of the circulation card (Tarjeta de Circulación).

        Determines whether the card is still valid based on three types of 
        validity representations: 'permanente', 'periodo' (in years), and 'fecha' 
        (exact expiration date). Compares the expiration date against the current date.

        Returns:
            bool: True if names match, False otherwise.
            str: A message indicating whether the circulation card is valid or not,
                with instructions for rejection and penalty in case of expiration.
        """
        mensaje_rechazo = 'Tarjeta de Ciruclación no vigente. Cotejar contra la tenencia del año en curso, si está pagada se da por default como vigente. Si no hay tenencias, se penaliza 3% valor factura. '
        if self.datos_tarjeta['Tipo de fecha de vigencia'] == 'permanente':
            return True, 'Tarjeta de Circulación vigente'
        if self.datos_tarjeta['Tipo de fecha de vigencia'] == 'periodo':
            periodo = self.extract_integers(self.datos_tarjeta['Valor de fecha de vigencia'])
            fecha_dt = datetime.strptime(self.datos_tarjeta['Fecha de expedición'], '%Y-%m-%d')
            nueva_fecha = fecha_dt + relativedelta(years=periodo)
            if nueva_fecha > datetime.datetime.now():
                return True, 'Tarjeta de Circulación vigente'
            else:
                return False, mensaje_rechazo
        if self.datos_tarjeta['Tipo de fecha de vigencia'] == 'fecha':
            fecha_vigencia = self.datos_tarjeta['Valor de fecha de vigencia']
            fecha_vigencia_dt = self.convertir_a_datetime(fecha_vigencia)
            if fecha_vigencia_dt > datetime.now():
                return True, 'Tarjeta de Circulación vigente'
            else:
                return False, mensaje_rechazo
        else:
            fecha_vigencia = self.datos_tarjeta['Fecha de vigencia']['valor']
            fecha_vigencia_dt = self.convertir_a_datetime(fecha_vigencia)
            if fecha_vigencia_dt > datetime.now():
                return True, 'Tarjeta de Circulación vigente'
            else:
                return False, mensaje_rechazo
        
    

    # Tarjeta 5.
    def valdiar_uso_vehiculo(self):
        """
        Validates the vehicle usage stated on the circulation card.

        Accepts only vehicles marked for "PARTICULAR" (private) use.
        Other usages lead to automatic rejection of the application.

        Returns:
            bool: True if names match, False otherwise.
            str: A message indicating whether the vehicle use is valid or the 
                application is rejected due to incorrect usage.
        """
        if 'PARTICULAR' in self.datos_tarjeta['Uso del vehículo'].upper().split():
            return True, 'Uso de vehículo correcto'
        else:
            return False, 'Trámite rechazado por uso de vehículo distinto a particular'
        

    # Tarjeta 6.
    def validar_adeudos(self):
        """
        Validates the presence of outstanding debts or infractions.

        Placeholder implementation assumes there are no debts.
        Future versions may check links to state databases for fines or taxes.

        Returns:
            bool: True if names match, False otherwise.
            str: A message confirming there are no outstanding debts on the
                circulation card.
        """
        # Revisar que no haya adeudos en links por estado
        # if infracciones == True:
        #     return 'Se penaliza el monto de la infracción'
        # if adeudos == True:
        #     return 'Se penaliza penaliza 3% por tenencia que no esté'
        return True, 'Sin adeudos en tarjeta de circulación'
    

    def data_validator_pipeline(self):
        """
        Runs a full validation pipeline on the provided document data.

        Sequentially invokes all individual validation methods to check:
        - Applicant name
        - Vehicle identification (NIV, motor number)
        - Vehicle data consistency
        - RFC match
        - SAT invoice comparison
        - Circulation card validity and usage
        - INE and endoso documents
        - Presence of debts or infractions

        Returns:
            dict: A dictionary mapping validation step names to their respective
                result messages.
        """
        validacion_nombre_bool, validacion_nombre_message = self.validar_nombre_solicitante()
        validacion_niv_bool, validacion_niv_message = self.validar_niv()
        validacion_datos_vehiculo_bool, validacion_datos_vehiculo_message = self.validar_datos_vehiculo()
        validacion_RFC_bool, validacion_RFC_message = self.validar_RFC()
        validacion_es_primera_emision_bool, validacion_es_primera_emision_message = self.validar_es_primera_emision()
        validacion_datos_SAT_bool, validacion_datos_SAT_message = self.validar_datos_SAT()
        validacion_no_motor_bool, validacion_no_motor_message = self.validar_no_motor()
        validacion_endoso_bool, validacion_endoso_message = self.validar_endoso()
        validacion_vigencia_INE_bool, validacion_vigencia_INE_message = self.validar_vigencia_INE()
        validacion_vigencia_tarjeta_bool, validacion_vigencia_tarjeta_message = self.validar_vigencia_tarjeta()
        validacion_uso_vehiculo_bool, validacion_uso_vehiculo_message = self.valdiar_uso_vehiculo()
        validacion_adeudos_bool, validacion_adeudos_message = self.validar_adeudos()

        # Collect all validation results    
        resultados_bool = {
            "validacion_nombre": validacion_nombre_bool,
            "validacion_niv": validacion_niv_bool,
            "validacion_datos_vehiculo": validacion_datos_vehiculo_bool,
            "validacion_RFC": validacion_RFC_bool,
            "validacion_es_primera_emision": validacion_es_primera_emision_bool,
            "validacion_datos_SAT": validacion_datos_SAT_bool,
            "validacion_no_motor": validacion_no_motor_bool,
            "validacion_endoso": validacion_endoso_bool,
            "validacion_vigencia_INE": validacion_vigencia_INE_bool,
            "validacion_vigencia_tarjeta": validacion_vigencia_tarjeta_bool,
            "validacion_uso_vehiculo": validacion_uso_vehiculo_bool,
            "validacion_adeudos": validacion_adeudos_bool
        }

        # Collect all validation messages
        resultados_message = {
            "validacion_nombre": validacion_nombre_message,
            "validacion_niv": validacion_niv_message,
            "validacion_datos_vehiculo": validacion_datos_vehiculo_message,
            "validacion_RFC": validacion_RFC_message,
            "validacion_es_primera_emision": validacion_es_primera_emision_message,
            "validacion_datos_SAT": validacion_datos_SAT_message,
            "validacion_no_motor": validacion_no_motor_message,
            "validacion_endoso": validacion_endoso_message,
            "validacion_vigencia_INE": validacion_vigencia_INE_message,
            "validacion_vigencia_tarjeta": validacion_vigencia_tarjeta_message,
            "validacion_uso_vehiculo": validacion_uso_vehiculo_message,
            "validacion_adeudos": validacion_adeudos_message
        }
        # Return the results
        return resultados_bool, resultados_message