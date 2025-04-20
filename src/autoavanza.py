import streamlit as st
import zipfile
import os
import pandas as pd
from functools import partial
import shutil
import hashlib
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
    classified_documents = []
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

                    classified_documents.append((document, new_file_name))
    
    return classified_documents

def get_file_hash(file):
    return hashlib.md5(file.getbuffer()).hexdigest()

# Streamlit interface x
st.title("Autoavanza")

st.container()
st.subheader("Clasificación de Documentos")

# Upload zip file
uploaded_file = st.file_uploader("Subir un archivo ZIP que contenga los documentos en PDF", type="zip")

if uploaded_file is not None:
    file_hash = get_file_hash(uploaded_file)

    # Check if it's a new upload
    if st.session_state.get("last_file_hash") != file_hash:
        st.session_state.last_file_hash = file_hash

        # Clean, unzip, and classify
        directory = decompress_zip(uploaded_file)
        st.success(f"Archivos decomprimidos correctamente")

        st.session_state.classified_documents = process_and_classify(directory)
    
    # Get the already-processed documents from session state
    classified_documents = st.session_state.get("classified_documents", [])

    # Sort and display
    sorted_documents = sorted(
        classified_documents,
        key=lambda x: display_order.index(x[0]) if x[0] in display_order else len(display_order)
    )

    st.markdown("## 📄 Documentos Clasificados")
    for document, filename in sorted_documents:
        with st.container():
            cols = st.columns([4, 2])
        with cols[0]:
            st.markdown(f"**📁 {document}**")
        with cols[1]:
            with open(filename, "rb") as pdf_file:
                PDFbyte = pdf_file.read()

            st.download_button(
                label="⬇️ Descargar",
                data=PDFbyte,
                file_name=document,
                mime="application/pdf",
                key=f"download_{document}_{filename}"
            )
