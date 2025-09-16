# Autoavanza

![image](https://github.com/user-attachments/assets/fe1b2b95-cbdb-4cea-bc8d-aa180b12f394)

**Autoavanza** is an application built with **Streamlit** that automates the extraction, classification, and validation of vehicle and official identification documents in Mexico. It is designed to optimize processes such as **vehicle pawn loans**, ensuring that submitted documents comply with regulations through intelligent processing and automated validation.

---

## 🧠 System Objectives

* Achieve at least **80% accuracy** in document extraction, classification, and validation.
* Reduce **document review time from 2 hours to less than 15 minutes**.
* Generate a **clear and precise ruling** in natural language in at least 80% of cases.

---

## 📌 System Modules

The system consists of the following main modules:

1. **Text Extraction**
   OCR-based system to detect and extract textual content from documents.

2. **File Classification**
   Automatic classification system that identifies the type of document based on OCR results.

3. **Data Extraction**
   Module that extracts key data from documents using an API (such as Gemini) from OCR content.

4. **QR Code Detection & Web Scraping**
   Detects QR codes in documents and extracts official information from the SAT portal using web scraping.

5. **Signature Detection**
   Identifies and extracts signatures present in documents.

6. **Signature Comparison**
   (In development) Compares detected signatures against a database or reference signature.

7. **Data Validation**
   Applies business rules for each document type, checking validity, data consistency, and more.

8. **Ruling**
   Generates a final validation ruling, useful for deciding whether to accept or reject the pawn loan process.

---

## 🚀 Results

### 📄 Document Classification

| Document              | Accuracy  |
| --------------------- | --------- |
| Invoice               | 100%      |
| Invoice Back          | 80%       |
| INE (ID card)         | 100%      |
| INE Back              | 90%       |
| Circulation Card      | 100%      |
| Circulation Card Back | 50%       |
| **Overall Accuracy:** | **92.3%** |

### 🧾 Data Extraction

* Extraction rate: **91.7%**
* Extracted values accuracy: **87.6%**

### ✅ Data Validation

* Completed checks: **94.4%**
* Accuracy with correct values: **100%**
* Accuracy with missing values: **70.6%**

### 🕒 Process Efficiency

* Previous time: **2 hours**
* With Autoavanza: **15 minutes**
* **87.5% reduction**

---

## 🛠️ Key Technologies

* **Python:** Main programming language.
* **Gemini API:** LLM used for flexible data extraction.
* **GitHub:** Version control and collaboration.
* **Streamlit:** Framework for building the interactive interface.

---

## 📁 Project Structure

```plaintext
Autoavanza/
├── README.md
├── assets/
│   ├── img/
│   │   └── logo.png              # Project logo with Monte de Piedad
│   └── videos/
│       └── DemoAutoavanza.mov    # Demonstration video
├── data/                         # Test cases in .zip format
├── src/                          # Processing and validation modules
│   ├── DataExtraction.py         # Extracts data from OCR text
│   ├── DataValidation.py         # Validates extracted data against business rules
│   ├── DocumentClassification.py # Automatic document classification
│   ├── OCR.py                    # OCR module
│   ├── QRExctraction.py          # QR detection + SAT scraping
│   ├── Ruling.py                 # Automated ruling generation
│   ├── SignatureComparison.py    # Automatic signature comparison
│   ├── SignatureStampValidation.py # Signature and stamp validation
│   ├── Staging.py                # Temporary storage and processing
│   ├── autoavanza.py             # Main Streamlit script
│   └── models/
│       └── best.pt               # Trained model (e.g., for signature detection)
└── temp/                         # Temporary processed files
    ├── archivos/                 # Decompressed documents
    ├── captchas/                 # SAT captchas
    └── signatures/               # Extracted document signatures
```

---

## ⚠️ Restrictions & Recommendations

* **Format:** documents must be uploaded as a `.zip` file.
* **Minimum content:** Invoice, INE, Circulation Card.
* **Orientation:** documents must be in vertical orientation.
* **Manual intervention:** required in case of classification, extraction, or signature errors.

---

## 🔄 Areas for Improvement

* Strengthen signature comparison with more data for production use.
* Define a robust confidence index for automatic acceptance/rejection.
* Improve date detection and validity checks.
* Add verification of **debts (Repuve & Transunion)** and **fiscal seals**.
* Optimize interface with a smoother framework.

---

## 🔮 Next Steps

* **Scale validation** with a larger sample to strengthen the signature model.
* **Design a confidence index** for automated decisions.
* **Add new rules** and additional validation checks.

---

## 🎥 System Demo

[Click here to watch the demo video](https://drive.google.com/file/d/1H7PF9Pwwyy-iesxNpx3tVy8nX80MXdGj/view?usp=sharing)


----

Spanish version 

# Autoavanza

![image](https://github.com/user-attachments/assets/fe1b2b95-cbdb-4cea-bc8d-aa180b12f394)

**Autoavanza** es una aplicación desarrollada con **Streamlit** que automatiza la extracción, clasificación y validación de documentos vehiculares y de identificación oficial en México. Está diseñada para optimizar procesos como el **empeño de vehículos**, garantizando que los documentos presentados cumplan con las normativas mediante procesamiento inteligente y validación automatizada.

---

## 🧠 Objetivos del sistema

* Lograr al menos un **80% de precisión** en la extracción, clasificación y validación de documentos.
* Reducir el **tiempo de revisión de documentos de 2 horas a menos de 15 minutos**.
* Generar un **dictamen claro y preciso** en lenguaje natural en al menos el 80% de los casos.

---

## 📌 Módulos del sistema

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

---

## 🚀 Resultados

### 📄 Clasificación de documentos

| Documento                         | Precisión |
| --------------------------------- | --------- |
| Factura                           | 100%      |
| Reverso de Factura                | 80%       |
| INE                               | 100%      |
| Reverso de INE                    | 90%       |
| Tarjeta de Circulación            | 100%      |
| Reverso de Tarjeta de Circulación | 50%       |
| **Precisión general:**            | **92.3%** |

### 🧾 Extracción de datos

* Porcentaje de extracción: **91.7%**
* Precisión de valores extraídos: **87.6%**

### ✅ Validación de datos

* Controles completados: **94.4%**
* Precisión con valores correctos: **100%**
* Precisión con valores faltantes: **70.6%**

### 🕒 Eficiencia del proceso

* Tiempo antes: **2 horas**
* Tiempo con Autoavanza: **15 minutos**
* **Reducción del 87.5%**

---

## 🛠️ Tecnologías clave

* **Python:** Lenguaje principal del sistema.
* **Gemini API:** LLM usado para extracción de datos flexibles.
* **GitHub:** Control de versiones y colaboración.
* **Streamlit:** Framework para desarrollo de la interfaz interactiva.

---

## 📁 Estructura del proyecto

```plaintext
Autoavanza/
├── README.md
├── assets/
│   ├── img/
│   │   └── logo.png              # Logo del proyecto con Monte de Piedad
│   └── videos/
│       └── DemoAutoavanza.mov    # Video demostrativo del funcionamiento
├── data/                         # Casos de prueba en formato .zip
├── src/                          # Módulos de procesamiento y validación
│   ├── DataExtraction.py         # Extracción de datos desde el texto OCR
│   ├── DataValidation.py         # Validación de datos extraídos según reglas del negocio
│   ├── DocumentClassification.py # Clasificación automática de documentos
│   ├── OCR.py                    # Módulo de OCR (Reconocimiento óptico de caracteres)
│   ├── QRExctraction.py          # Detección y extracción de QR + scraping SAT
│   ├── Ruling.py                 # Generación del dictamen automatizado
│   ├── SignatureComparison.py    # Comparación automática de firmas
│   ├── SignatureStampValidation.py # Validación de firmas y sellos
│   ├── Staging.py                # Almacenamiento y procesamiento intermedio
│   ├── autoavanza.py             # Script principal para ejecutar el flujo en Streamlit
│   └── models/
│       └── best.pt               # Modelo entrenado (por ejemplo, para detección de firmas)
└── temp/                         # Archivos temporales procesados
    ├── archivos/                 # Documentos decomprimidos
    ├── captchas/                 # Captchas del SAT
    └── signatures/               # Firmas extraídas desde los documentos

```

---

## ⚠️ Restricciones y recomendaciones

* **Formato:** los documentos deben subirse en un archivo `.zip`.
* **Contenido mínimo:** Factura, INE, Tarjeta de Circulación.
* **Orientación:** Los documentos deben estar en orientación vertical.
* **Intervención manual:** en caso de fallas en clasificación, extracción o firmas.

---

## 🔄 Áreas de mejora

* Validar la comparación de firmas con más datos para uso en producción.
* Definir un índice de confianza robusto para aceptación/rechazo automático.
* Mejorar la detección de fechas y validación de vigencias.
* Incluir verificación de **adeudos (Repuve y Transunion)** y **sellos fiscales**.
* Optimizar la interfaz con un framework más fluido.

---

## 🔮 Siguientes pasos

* **Escalar validación** con una muestra más amplia para robustecer el modelo de firmas.
* **Diseñar un índice de confianza** para decisiones automáticas.
* **Incorporar nuevas reglas** y controles de validación adicionales.

---

## 🎥 Demo del sistema

[Haz clic aquí para ver la demostración en video](https://drive.google.com/file/d/1H7PF9Pwwyy-iesxNpx3tVy8nX80MXdGj/view?usp=sharing)





