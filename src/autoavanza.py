import streamlit as st
import zipfile
import os
import pandas as pd
from functools import partial
import shutil
import OCR
import DocumentClassification

@st.cache_data
def decompress_zip(zip_file):
# Get the absolute path to the root directory (one level up from this file)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(root_dir, "temp", "archivos")

    os.makedirs(output_dir, exist_ok=True)

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    return output_dir

@st.cache_data
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

# Streamlit interface
st.title("Autoavanza")

st.container()
st.subheader("Clasificación de Documentos")

# Upload zip file
uploaded_file = st.file_uploader("Subir un archivo ZIP que contenga los documentos en PDF", type="zip")

# Custom display order
display_order = [
        "FACTURA",
        "FACTURA_REVERSO",
        "INE",
        "INE_REVERSO",
        "TARJETA_CIRCULACION",
        "TARJETA_CIRCULACION_REVERSO",
        "REVISAR"
        ]

if uploaded_file is not None:
    # Decompress files
    directory = decompress_zip(uploaded_file)
    st.success(f"Archivos decomprimidos correctamente")

    # Store all classified documents as (document_type, filename) pairs
    classified_documents = process_and_classify(directory)

    # Sort documents by the defined display order
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
            st.caption(f"Archivo: {filename}")

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
            
    # Button to clear temporary files
    if st.button("🗑️ Limpiar Archivos Temporales"):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        temp_dir = os.path.join(root_dir, "temp")
        archivos_dir = os.path.join(temp_dir, "archivos")
        try:
            if os.path.exists(archivos_dir):
                shutil.rmtree(archivos_dir)
                st.success("¡Archivos temporales eliminados!")
            else:
                st.info("No hay archivos temporales para eliminar.")
        except Exception as e:
            st.error(f"Ocurrió un error al eliminar los archivos temporales: {e}")

