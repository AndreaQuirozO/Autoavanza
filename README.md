# Autoavanza

![image](https://github.com/user-attachments/assets/fe1b2b95-cbdb-4cea-bc8d-aa180b12f394)

**Autoavanza** es una aplicación desarrollada con **Streamlit** que automatiza la extracción, clasificación y validación de documentos vehiculares y de identificación oficial en México. Está diseñada para optimizar procesos como el **empeño de vehículos**, garantizando que los documentos presentados cumplan con las normativas mediante procesamiento inteligente y validación automatizada.

## 📌 Etapas del sistema

El sistema está compuesto por los siguientes módulos principales:

1. **Extracción de texto**  
   Sistema de extracción de texto usando Reconocimiento Óptico de Caracteres (OCR) para detectar y extraer contenido textual de documentos.

2. **Clasificación de archivos**  
   Sistema de clasificación automática que identifica el tipo de documento en función de su contenido textual obtenido del OCR.

3. **Extracción de datos**  
   Módulo que extrae los datos clave de los documentos utilizando una API (como Gemini) a partir del contenido OCR.

4. **Detector de código QR y web scraping**  
   Sistema que detecta códigos QR en los documentos y extrae información oficial desde el portal del SAT usando técnicas de web scraping.

5. **Detección de firma**  
   Módulo para identificar y extraer la firma presente en los documentos.

6. **Comparación de firmas**  
   Sistema (en desarrollo) para contrastar la firma detectada con una base de datos o firma de referencia.

7. **Validación de datos**  
   Sistema de validación que aplica reglas del negocio definidas para cada tipo de documento, evaluando vigencia, coincidencias de datos y más.

8. **Certamen**  
   Genera un dictamen final del proceso de validación, útil para decidir la aceptación o rechazo del trámite de empeño.


## 📁 Estructura del proyecto

```
Autoavanza                  
├── .gitignore              
├── README.md               
├── assets                  
│   └── img
│       └── logo.png        # Logo for proyect with Monte de Piedad
├── data                    # Sample input data or test cases for processing
│   ├── Caso 12.zip         # Compressed folder with documents for case 12
│   └── Caso 6.zip          # Compressed folder with documents for case 6
├── src                     
│   ├── DataExtraction.py           # Extracts key information from OCR output
│   ├── DocumentClassification.py   # Classifies documents based on extracted text
│   ├── OCR.py                      # Module to perform OCR (Optical Character Recognition) on documents
│   ├── QRExctraction.py            # Detects and decodes QR codes from images
│   ├── Staging.py                  # Handles intermediate storage or data preprocessing
│   └── autoavanza.py               # Main script to run the full pipeline using streamlit
└── temp                            # Temporary folder used to store processed files and intermediate outputs
    ├── archivos                    # Decompressed and organized documents for a specific case
    │   └── Caso 12
    │       ├── TK 61417-1_FACTURA.pdf                     # Vehicle invoice (front)
    │       ├── TK 61417-2_FACTURA REVERSO.pdf             # Vehicle invoice (back)
    │       ├── TK 61417-3_INE.pdf                         # INE (voter ID) front side
    │       ├── TK 61417-4_INE REVERSO.pdf                 # INE back side
    │       ├── TK 61417-5_TARJETA CIRCULACION.pdf         # Circulation card front side
    │       └── TK 61417-6_TARJETA CIRCULACION REVERSO.pdf # Circulation card back side
    └── captchas
        └── captcha.png     # CAPTCHA image to validate document authenticity with external services