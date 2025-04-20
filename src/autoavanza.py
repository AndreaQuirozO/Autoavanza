import streamlit as st
import zipfile
import os
import pandas as pd
from functools import partial
import shutil
import hashlib
import base64
from streamlit_pdf_viewer import pdf_viewer

import OCR
import DocumentClassification

display_order = [
    "FACTURA",
    "FACTURA_REVERSO",
    "INE",
    "INE_REVERSO",
    "TARJETA_CIRCULACION",
    "TARJETA_CIRCULACION_REVERSO",
    "REVISAR"
]

def decompress_zip(zip_file):
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(root_dir, "temp", "archivos")

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

    return output_dir

def process_and_classify(directory):
    classified_documents = {}
    for folder in os.listdir(directory):
        if folder not in ['.DS_Store', '__MACOSX']:
            for filename in os.listdir(os.path.join(directory, folder)):
                if filename.endswith(".pdf") and filename != '.DS_Store':
                    pdf_path = os.path.join(directory, folder, filename)
                    image_path = OCR.convert_pdf_to_image(pdf_path)
                    results = OCR.image_to_text(image_path)
                    new_file_name, document = DocumentClassification.classify_document(results, image_path)
                    os.rename(pdf_path, new_file_name)
                    os.remove(image_path)
                    classified_documents[os.path.basename(new_file_name)] = {"type": document, "filename": new_file_name}
    return classified_documents

def get_file_hash(file):
    return hashlib.md5(file.getbuffer()).hexdigest()

# Streamlit interface
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("# 🚗 Autoavanza 🚗")

st.markdown("## ⬆️ Carga de Documentos")

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

        st.markdown("## 📄 Revisar y Confirmar Clasificación")

        document_types = [
            "FACTURA", "FACTURA_REVERSO", "INE", "INE_REVERSO",
            "TARJETA_CIRCULACION", "TARJETA_CIRCULACION_REVERSO", "REVISAR"
        ]

        updated_documents_data = {}

        for item_key, doc_info in sorted_documents_list:
            current_filename = doc_info["filename"]
            current_type = doc_info["type"]
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
                        updated_documents_data[item_key] = {"type": selected_type, "filename": new_filename}
                    else:
                        updated_documents_data[item_key] = {"type": current_type, "filename": current_filename}
                        st.info("No se realizaron cambios.")
                else:
                    updated_documents_data[item_key] = {"type": current_type, "filename": current_filename}

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