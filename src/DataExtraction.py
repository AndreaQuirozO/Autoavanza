import re
from datetime import datetime
from dotenv import load_dotenv
from google import genai
import json

def call_gemini(api_key: str, system_message: str, input_message: str):
    prompt = f"{system_message}\n\nTexto extraído del documento:\n{input_message}\n\nPor favor, responde solo con el JSON correspondiente."
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response

class BaseDataExtractor:
    def __init__(self, texto, api_key):
        self.texto = texto
        self.api_key = api_key
        self.system_message = ""  # To be overridden in subclass

    def parse_json(self, response):
        json_response = response.model_dump_json()
        json_data = json.loads(json_response)
        json_processed = json_data['candidates'][0]['content']['parts'][0]['text']
        content = json_processed.strip("```json\n").strip("```")
        parsed_json = json.loads(content)
        return parsed_json

    def extraer_datos(self):
        response = call_gemini(self.api_key, self.system_message, self.texto)
        return self.parse_json(response)

class INEDataExtractor(BaseDataExtractor):
    def __init__(self, texto, api_key):
        super().__init__(texto, api_key)
        self.system_message = """
            Eres un experto en análisis de documentos semiestructurados en español, especialmente en credenciales del INE (Instituto Nacional Electoral) mexicanas.  
            Tu tarea es leer cuidadosamente el contenido proporcionado y extraer la siguiente información clave.  
            Es **muy importante** que mantengas exactamente los mismos nombres de claves que se indican a continuación y no agregues ninguna clave adicional.  
            Si la información no está presente en el documento, indica el valor como 'N/A'.

            Claves requeridas y su descripción:
            1. Nombre del solicitante: Nombre completo de la persona titular de la credencial del INE.
            2. Vigencia: Fecha de vigencia indicada en la credencial. Ejemplo: "2029", "2032".
            3. Vigente: Indica si la credencial está vigente usando el año de vigencia. Debe estar como True o False.
            4. Clave de elector: Clave alfanumérica asignada por el INE a cada ciudadano.

            Guías adicionales:
            - Solo extrae lo que esté explícitamente presente en el documento.
            - No infieras ni completes información por tu cuenta. Si algún campo no está disponible, indica 'N/A'.
        """


class FacturaDataExtractor(BaseDataExtractor):
    def __init__(self, texto, api_key):
        super().__init__(texto, api_key)
        self.system_message = """
            Eres un experto en análisis de documentos semiestructurados en español, especialmente en facturas de vehículos.  
            Tu tarea es leer cuidadosamente el contenido proporcionado y extraer la siguiente información clave.  
            Es **muy importante** que mantengas exactamente los mismos nombres de claves que se indican a continuación y no agregues ninguna clave adicional.  
            Si la información no está presente en el documento, indica el valor como 'N/A'.

            Claves requeridas y su descripción:
            1. Nombre del solicitante: Nombre completo de la persona que solicita el trámite o aparece como titular en la factura.  
            2. Marca: Marca del vehículo. Ejemplo: "Nissan", "Toyota".  
            3. Modelo: Modelo del vehículo. Ejemplo: "Versa", "Hilux".  
            4. Año: Año del vehículo. Ejemplo: "2020", "2023".  
            5. Versión: Versión o submodelo del vehículo. Ejemplo: "Sense", "LE 4x4".  
            6. Número de motor: Número de identificación del motor del vehículo.  
            7. NIV: Número de Identificación Vehicular (también conocido como número de serie).  
            8. Leyenda primera emisión: Texto (o parte del texto) que indique que el documento es la primera emisión, por ejemplo: “El presente documento se da como primera impresión...”  
            9. Cadena original del complemento de certificación digital del SAT: Texto completo de la cadena original que aparece en la parte inferior del documento y que corresponde a la certificación digital del SAT.

            Guías adicionales:
            - Solo extrae lo que esté explícitamente presente en el documento, incluso si está en una sección separada o difícil de leer.  
            - No infieras ni completes información por tu cuenta. Si algún campo no está disponible, indica 'N/A'.
    """



class FacturaReversoDataExtractor(BaseDataExtractor):
    def __init__(self, texto, api_key):
        super().__init__(texto, api_key)
        self.system_message = """
            Eres un experto en análisis de documentos semiestructurados en español, especialmente en el reverso de facturas de vehículos.  
            Tu tarea es leer cuidadosamente el contenido proporcionado y extraer la siguiente información clave.  
            Es **muy importante** que mantengas exactamente el mismo nombre de la clave que se indica a continuación y no agregues ninguna clave adicional.  
            Si la información no está presente en el documento, indica el valor como 'N/A'.

            Clave requerida y su descripción:
            1. Nombre del nuevo dueño: Nombre completo de la persona a quien se ha endosado el vehículo, en caso de que exista un endoso. Esta información suele estar escrita a mano en el reverso de la factura.

            Guías adicionales:
            - Solo extrae lo que esté explícitamente presente en el documento, incluso si está escrito a mano.
            - No infieras ni completes información por tu cuenta. Si el campo no está disponible, indica 'N/A'.

        """


class TarjetCirculacionDataExtractor(BaseDataExtractor):
    def __init__(self, texto, api_key):
        super().__init__(texto, api_key)
        self.system_message = """
            Eres un experto en análisis de documentos semiestructurados en español, especialmente en tarjetas de circulación vehicular en México.  
            Tu tarea es leer cuidadosamente el contenido proporcionado y extraer la siguiente información clave.  
            Es **muy importante** que mantengas exactamente los mismos nombres de claves que se indican a continuación y no agregues ninguna clave adicional.  
            Si la información no está presente en el documento, indica el valor como 'N/A'.

            Claves requeridas y su descripción:
            1. Nombre del solicitante: Nombre completo del titular de la tarjeta de circulación.  
            2. Fecha de vigencia del año en curso: Fecha de vencimiento de la tarjeta correspondiente al año actual.  
            3. NIV: Número de Identificación Vehicular.  
            4. Número de motor: Número de serie del motor del vehículo.  
            5. Marca: Marca del vehículo. Ejemplo: "Volkswagen", "Chevrolet", "KIA".  
            6. Modelo: Modelo del vehículo. Ejemplo: "Jetta", "Aveo".  
            7. Año: Año del vehículo. Ejemplo: "2020", "2023".

            Guías adicionales:
            - Solo extrae lo que esté explícitamente presente en el documento, aunque el texto esté en mayúsculas, parcialmente ilegible o mal alineado.  
            - No infieras ni completes información por tu cuenta. Si algún campo no está disponible, indica 'N/A'.

        """
