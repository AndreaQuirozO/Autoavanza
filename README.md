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

[Click here to watch the demo video](https://drive.google.com/file/d/15qfzfWAubFuh77JC4_LL6NKktIxQcv8P/view?usp=sharing






