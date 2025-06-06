from google import genai
import os
from dotenv import load_dotenv
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
import tempfile
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import tempfile
import re
import markdown
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd


load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def call_gemini(api_key: str, system_message: str, data_results_message: dict, data_results_bool: dict, sign_results_message: dict, sign_results_bool: dict):
    """
    Calls the Gemini API to generate content based on validation results.

    Args:
        api_key (str): API key for Gemini.
        system_message (str): Instruction prompt describing the assistant's role and context.
        data_results_message (dict): Dictionary with explanatory messages for each data validation.
        data_results_bool (dict): Dictionary with boolean results of data validations.
        sign_results_message (dict): Dictionary with explanatory messages for signature validations.
        sign_results_bool (dict): Dictionary with boolean results of signature validations.

    Returns:
        genai.types.GenerateContentResponse: The response generated by the Gemini model.
    """
    prompt = f"{system_message}\n\nDiccionarios con los resultados:\n{data_results_message}\n\n{data_results_bool}\n\n{sign_results_message}\n\n{sign_results_bool}\n\n"
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response

class RulingMaker:
    """
    Class responsible for generating a legal ruling based on validation results
    of document data and signatures using the Gemini API.

    Methods:
        parse_json(response): Extracts and returns the generated text from the JSON response.
        obtener_dictamen(): Runs the full pipeline to generate a decision from the input data.
    """
    def __init__(self, data_results_message, data_results_bool, sign_results_message, sign_results_bool, api_key):
        """
        Initializes the RulingMaker object.

        Args:
            data_results_message (dict): Messages explaining the outcome of each data validation.
            data_results_bool (dict): Boolean results of data validations.
            sign_results_message (dict): Messages explaining the outcome of each signature validation.
            sign_results_bool (dict): Boolean results of signature validations.
            api_key (str): API key for Gemini authentication.
        """
        self.data_results_message = data_results_message
        self.data_results_bool = data_results_bool
        self.sign_results_message = sign_results_message
        self.sign_results_bool = sign_results_bool
        self.api_key = api_key
        self.system_message = """
            Eres un asistente legal y administrativo experto encargado de analizar los resultados de validación de documentos relacionados con un vehículo en el contexto de un proceso de empeño.

            Recibirás cuatro diccionarios como entrada:

            data_results_message: diccionario con mensajes que explican el resultado de cada validación de datos.
            data_results_bool: diccionario con valores booleanos (True o False) que indican si cada validación de datos fue superada.
            sign_results_message: diccionario con mensajes que explican el resultado de cada validación de firmas.
            sign_results_bool: diccionario con valores booleanos (True o False) que indican si cada validación de firmas fue superada.
            Los cuatro diccionarios comparten la misma estructura: cada clave representa una validación específica, y su valor correspondiente indica el resultado (mensaje o booleano).

            Tu tarea es generar un fallo conciso que resuma el resultado de todas las validaciones e indique si el vehículo puede ser empeñado.

            Si todos los valores booleanos son True, devuelve un mensaje positivo y claro indicando que el vehículo puede ser empeñado.
            Si algún valor booleano es False, debes indicar claramente:
            Que el vehículo no puede ser empeñado,
            Cuáles validaciones fallaron (en viñetas), y
            Por qué fallaron, utilizando los mensajes correspondientes de los diccionarios *_results_message.
            Cuando un mensaje indica que no se encuontró firma ya sea en el Reverso de Factura, Tarjeta de circulación o INE, menciona que se requiere intervención humana para validar la(s) firma(s) faltante(s).
            Indica claramente en el dictamen que se deben validar manualmente los adeudos del vehículo.
            Importante: No comiences el texto con la palabra “Dictamen”, ya que será añadida como título por separado.

            Estructura la respuesta en uno a tres párrafos breves como máximo. Sé formal, preciso y evita repeticiones innecesarias.   
        """ 

    @staticmethod
    def prettify_key_spanish(key):
        mapping = {
            "validacion": "Validación",
            "nombre": "Nombre",
            "niv": "NIV",
            "datos": "Datos",
            "vehiculo": "Vehículo",
            "RFC": "RFC",
            "es": "Es",
            "primera": "Primera",
            "emision": "Emisión",
            "sat": "SAT",
            "no": "No",
            "motor": "Motor",
            "endoso": "Endoso",
            "vigencia": "Vigencia",
            "ine": "INE",
            "tarjeta": "Tarjeta",
            "circulacion": "Circulación",
            "uso": "Uso",
            "adeudos": "Adeudos",
            "firma": "Firma",
            "sello": "Sello",
            "reverso": "Reverso"
        }

        words = key.split("_")
        pretty_words = [mapping.get(word, word.capitalize()) for word in words]
        return " ".join(pretty_words)
    
    @staticmethod
    def clean_markdown(text):
        # Remove * _ ** and other markdown formatting characters
        return re.sub(r'[*_`#>-]', '', text).strip()
    
    @staticmethod
    def markdown_to_paragraph(md_text):
        styles = getSampleStyleSheet()
        styleN = styles["Normal"]
        html_text = markdown.markdown(md_text)
        return Paragraph(html_text, styleN)
    
    def build_validation_dataframe(self, message_dict, bool_dict):
        rows = []
        for key in message_dict:
            cumple = "Sí" if bool_dict[key] else "No"
            mensaje = message_dict[key]
            if isinstance(mensaje, dict):
                mensaje = list(mensaje.values())[0]
            rows.append({
                "Validación": self.prettify_key_spanish(key),
                "¿Cumple?": cumple,
                "Mensaje": mensaje
            })
        return pd.DataFrame(rows)


    def parse_json(self, response):
        """
        Extracts the generated text from the Gemini JSON response.

        Args:
            response (genai.types.GenerateContentResponse): Response from the Gemini API.

        Returns:
            str: The processed and extracted text generated by the model.
        """
        json_response = response.model_dump_json()
        json_data = json.loads(json_response)
        json_processed = json_data['candidates'][0]['content']['parts'][0]['text']
        return json_processed
    
    def obtener_dictamen(self):
        """
        Executes the full pipeline to generate a ruling using the Gemini API.

        Returns:
            str: The final decision generated based on validation results.
        """
        response = call_gemini(
            self.api_key, 
            self.system_message, 
            self.data_results_message, 
            self.data_results_bool, 
            self.sign_results_message, 
            self.sign_results_bool
        )
        self.response = self.parse_json(response)
        return self.response


    def generar_pdf_dictamen(self):
        styles = getSampleStyleSheet()
        styleN = styles["BodyText"]

        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        file_path = tmp_file.name

        doc = SimpleDocTemplate(file_path, pagesize=LETTER)
        elements = []

        title = Paragraph("<b>Dictamen de Validación de Documentos</b>", styles["Title"])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Encabezados de tabla
        data = [["Validación", "¿Cumple?", "Mensaje"]]

        # Función para añadir filas
        def add_rows(message_dict, bool_dict):
            for key in message_dict:
                cumple = "Sí" if bool_dict[key] else "No"
                mensaje = message_dict[key]
                if isinstance(mensaje, dict):
                    mensaje = list(mensaje.values())[0]
                data.append([
                    Paragraph(self.prettify_key_spanish(key), styleN),
                    Paragraph(cumple, styleN),
                    Paragraph(mensaje, styleN)
                ])

        add_rows(self.data_results_message, self.data_results_bool)
        add_rows(self.sign_results_message, self.sign_results_bool)

        table = Table(data, colWidths=[120, 50, 350])  # ajusta ancho de columnas
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#CCCCCC")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (1, 1), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))

        elements.append(table)
        if not hasattr(self, 'response'):
            self.response = self.obtener_dictamen()
        
        elements.append(Spacer(1, 24))
        dictamen_title = Paragraph("<b>Conclusión</b>", styles["Heading2"])
        dictamen_text = self.markdown_to_paragraph(self.response)
        elements.extend([dictamen_title, Spacer(1, 6), dictamen_text])

        doc.build(elements)

        return file_path
    

    def return_table_dictamen(self):
        # Combine both sets of results
        df_data = self.build_validation_dataframe(self.data_results_message, self.data_results_bool)
        df_sign = self.build_validation_dataframe(self.sign_results_message, self.sign_results_bool)

        # Combine into one DataFrame
        df_total = pd.concat([df_data, df_sign], ignore_index=True)

        return df_total

