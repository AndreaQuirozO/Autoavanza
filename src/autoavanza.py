import streamlit as st
import zipfile
import os
import pandas as pd
from functools import partial
import shutil
import json
from dotenv import load_dotenv
from google import genai
import hashlib
import base64
from streamlit_pdf_viewer import pdf_viewer
from PIL import Image

from OCR import DataExtractor
from DocumentClassification import DocumentClassifier
from Staging import Staging
from QRExctraction import CFDIValidator
from DataExtraction import INEDataExtractor, FacturaDataExtractor, FacturaReversoDataExtractor, TarjetCirculacionDataExtractor


load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

display_order = [
    "FACTURA",
    "FACTURA REVERSO",
    "INE",
    "INE REVERSO",
    "TARJETA CIRCULACION",
    "TARJETA CIRCULACION REVERSO",
    "REVISAR"
]

logo_path = "../assets/img/logo.png"


def decompress_zip(zip_file):
    staging = Staging("archivos")
    staging_path = staging.run()

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(staging_path)

    return staging_path

def process_and_classify(directory):
    classified_documents = {}
    for folder in os.listdir(directory):
        if folder not in ['.DS_Store', '__MACOSX']:
            for filename in os.listdir(os.path.join(directory, folder)):
                if filename.endswith(".pdf") and filename != '.DS_Store':
                    pdf_path = os.path.join(directory, folder, filename)
                    data_extractor = DataExtractor()
                    image_path = data_extractor.convert_pdf_to_image(pdf_path)
                    results = data_extractor.image_to_text(image_path)
                    # data_extractor.delete_image(image_path)
                    document_classifier = DocumentClassifier(image_path, results)
                    new_file_name, document = document_classifier.classify()
                    os.rename(pdf_path, new_file_name)
                    os.remove(image_path)
                    classified_documents[os.path.basename(new_file_name)] = {"type": document, "filename": new_file_name, "text": results}
    return classified_documents

def get_file_hash(file):
    return hashlib.md5(file.getbuffer()).hexdigest()

# Streamlit interface
logo = Image.open(logo_path)
st.set_page_config( page_title='Autoavanza', page_icon=logo)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo_path)  # Adjust width as needed

st.container()
st.markdown("## Carga de Documentos")

# Upload zip file
uploaded_file = st.file_uploader("Subir un archivo ZIP que contenga los documentos en PDF", type="zip")

if uploaded_file is not None:
    file_hash = get_file_hash(uploaded_file)

    if st.session_state.get("last_file_hash") != file_hash:
        st.session_state.last_file_hash = file_hash
        directory = decompress_zip(uploaded_file)
        st.success(f"Archivos decomprimidos correctamente")
        st.session_state.classified_documents_data = process_and_classify(directory)

    classified_documents_data = st.session_state.get("classified_documents_data", {})

    if classified_documents_data:
        # Convert to a list for sorting and display
        classified_documents_list = list(classified_documents_data.items())

        def sort_key(item):
            return display_order.index(item[1]["type"]) if item[1]["type"] in display_order else len(display_order)

        sorted_documents_list = sorted(classified_documents_list, key=sort_key)
        print(sorted_documents_list)

        st.markdown("## 📄 Revisar y Confirmar Clasificación")

        document_types = [
            "FACTURA", "FACTURA REVERSO", "INE", "INE REVERSO",
            "TARJETA CIRCULACION", "TARJETA CIRCULACION REVERSO", "REVISAR"
        ]

        updated_documents_data = {}

        for item_key, doc_info in sorted_documents_list:
            current_filename = doc_info["filename"]
            current_type = doc_info["type"]
            current_text = doc_info["text"]
            base_filename = os.path.basename(current_filename)

            if not os.path.exists(current_filename):
                st.error(f"No se encontró el archivo: {current_filename}")
                continue

            with st.expander(f"{current_type}", expanded=False):
                if os.path.exists(current_filename):
                    pdf_viewer(current_filename)
                else:
                    st.error(f"No se encontró el archivo: {current_filename}")
                    continue

                selected_type = st.selectbox(
                    "Tipo de documento:",
                    options=document_types,
                    index=document_types.index(current_type),
                    key=f"select_{base_filename}"  # Use a stable key
                )

                if st.button("💾 Guardar Cambios", key=f"save_{base_filename}"):
                    if selected_type != current_type:
                        new_filename = os.path.join(os.path.dirname(current_filename), base_filename.replace(current_type, selected_type))
                        os.rename(current_filename, new_filename)
                        st.success(f"Archivo renombrado a: {os.path.basename(new_filename)}")
                        updated_documents_data[item_key] = {"type": selected_type, "filename": new_filename, "text": current_text}
                    else:
                        updated_documents_data[item_key] = {"type": current_type, "filename": current_filename, "text": current_text}
                        st.info("No se realizaron cambios.")
                else:
                    updated_documents_data[item_key] = {"type": current_type, "filename": current_filename, "text": current_text}

                if os.path.exists(current_filename):
                    with open(current_filename, "rb") as pdf_file:
                        PDFbyte = pdf_file.read()
                    st.download_button(
                        label="⬇️ Descargar",
                        data=PDFbyte,
                        file_name=os.path.basename(current_filename),
                        mime="application/pdf",
                        key=f"download_{base_filename}"
                    )

        # Update the session state with the potentially renamed files
        st.session_state.classified_documents_data.update(updated_documents_data)
        print(st.session_state.classified_documents_data)
        
        if st.button("✅ Apruebo Clasificación", key="aprobacion_clasificacion"):
            factura_file = None
            for doc_info in st.session_state.classified_documents_data.values():
                if doc_info["type"] == "FACTURA":
                    factura_file = doc_info["filename"]
                    break
                if doc_info["type"] == "FACTURA REVERSO":
                    factura_reverso_file = doc_info["filename"]
                    break
                if doc_info["type"] == "INE":
                    factura_file = doc_info["filename"]
                    break
                if doc_info["type"] == "INE REVERSO":
                    factura_file = doc_info["filename"]
                    break
                if doc_info["type"] == "TARJETA CIRCULACION":
                    factura_file = doc_info["filename"]
                    break
                if doc_info["type"] == "TARJETA CIRCULACION REVERSO":
                    factura_file = doc_info["filename"]
                    break
                

            if factura_file and os.path.exists(factura_file):
                validator = CFDIValidator(factura_file)
                urls = validator.extract_url_from_qr()

                if urls:
                    st.success("Código QR encontrado en factura.")
                    validator.open_browser(urls[0])

                    captcha_path = validator.save_captcha_image_for_streamlit()

                    if os.path.exists(captcha_path):
                        st.session_state.validator = validator
                        st.session_state.captcha_path = captcha_path
                        st.session_state.captcha_attempts = 0

            else:
                st.error("⚠️ No se encontró ningún archivo clasificado como FACTURA.")

            
            if factura_reverso_file and os.path.exists(factura_reverso_file):
                validator = CFDIValidator(factura_reverso_file)
                urls = validator.extract_url_from_qr()

                if urls:
                    st.success("Código QR encontrado en factura reverso.")
                    validator.open_browser(urls[0])

                    captcha_path = validator.save_captcha_image_for_streamlit()

                    if os.path.exists(captcha_path):
                        st.session_state.validator = validator
                        st.session_state.captcha_path = captcha_path
                        st.session_state.captcha_attempts = 0


    if "validator" in st.session_state and "captcha_path" in st.session_state:
        with st.form(key="captcha_form"):
            st.image(st.session_state.captcha_path, caption="Ingrese el código CAPTCHA")
            
            input_key = f"captcha_input_{st.session_state.captcha_attempts}"
            user_code = st.text_input("Código CAPTCHA", key=input_key)

            if st.form_submit_button("🔐 Validar Código"):
                st.session_state.captcha_attempts += 1
                datos_factura = st.session_state.validator.extract_data_with_code(user_code)

                if datos_factura:
                    st.success("✅ Datos extraídos correctamente:")
                    st.json(datos_factura)
                    st.session_state.validator.close_browser()
                    for key in ["captcha_attempts", "validator", "captcha_path"]:
                        del st.session_state[key]
                else:
                    if st.session_state.captcha_attempts < 3:
                        st.warning(f"Intento {st.session_state.captcha_attempts}/3 fallido. Intenta nuevamente.")
                        new_path = st.session_state.validator.save_captcha_image_for_streamlit()
                        st.session_state.captcha_path = new_path
                        st.rerun()
                    else:
                        st.error("❌ Se alcanzó el número máximo de intentos.")
                        st.session_state.validator.close_browser()
                        for key in ["captcha_attempts", "validator", "captcha_path"]:
                            del st.session_state[key]


