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

[Haz clic aquí para ver la demostración en video](## 🎥 Demo del sistema

👉 [Haz clic aquí para ver la demostración en video](https://www.youtube.com/watch?v=your_video_id)
)





