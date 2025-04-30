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
├── README.md
├── assets
│   └── img
│       └── logo.png
├── data
│   ├── Caso 12.zip
│   └── Caso 6.zip
├── src
│   ├── DataExtraction.py
│   ├── DocumentClassification.py
│   ├── OCR.py
│   ├── QRExctraction.py
│   ├── Staging.py
│   └── autoavanza.py
└── temp
    ├── archivos
    │   ├── Caso 12
    │   │   ├── TK 61417-1_FACTURA.pdf
    │   │   ├── TK 61417-2_FACTURA REVERSO.pdf
    │   │   ├── TK 61417-3_INE.pdf
    │   │   ├── TK 61417-4_INE REVERSO.pdf
    │   │   ├── TK 61417-5_TARJETA CIRCULACION.pdf
    │   │   └── TK 61417-6_TARJETA CIRCULACION REVERSO.pdf
    │   └── __MACOSX
    │       └── Caso 12
    └── captchas
        └── captcha.png
Autoavanza/
├── data/                # Datos de entrada y ejemplos de documentos
├── src/                 # Código fuente principal
│   ├── ocr/             # Módulos relacionados con OCR
│   ├── classification/  # Lógica de clasificación de documentos
│   ├── validation/      # Reglas y lógica de validación
│   └── app.py           # Aplicación principal de Streamlit
├── temp/                # Archivos temporales generados durante la ejecución
├── requirements.txt     # Dependencias del proyecto
└── README.md            # Documentación del proyecto
```

## 🚀 Instalación y ejecución

1. **Clonar el repositorio**:

   ```bash
   git clone https://github.com/AndreaQuirozO/Autoavanza.git
   cd Autoavanza
   ```

2. **Crear y activar un entorno virtual (opcional pero recomendado)**:

   ```bash
   python -m venv env
   source env/bin/activate  # En Windows: env\Scripts\activate
   ```

3. **Instalar las dependencias**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**:

   ```bash
   streamlit run src/app.py
   ```

## 🧪 Ejemplo de uso

1. Inicia la aplicación y carga una imagen o PDF de un documento.
2. El sistema extraerá el texto utilizando OCR.
3. Clasificará automáticamente el tipo de documento.
4. Aplicará las reglas de validación correspondientes y mostrará los resultados en pantalla.

## 📌 Tecnologías utilizadas

- **Python 3.8+**
- **Streamlit**: Para la creación de la interfaz web interactiva.
- **Tesseract OCR**: Motor de OCR para la extracción de texto.
- **scikit-learn**: Para la clasificación de documentos.
- **Pandas y NumPy**: Para el manejo y análisis de datos. ([ses4255/Versatile-OCR-Program - GitHub](https://github.com/ses4255/Versatile-OCR-Program?utm_source=chatgpt.com))

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

¿Te gustaría que incluya una sección con capturas de pantalla o ejemplos visuales para mejorar la presentación? 