import streamlit as st
import zipfile
import os
import pandas as pd
from functools import partial
import shutil
import OCR
import DocumentClassification

# Function to decompress zip file
def decompress_zip(zip_file):
    output_dir = "temp/archivos"
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    return output_dir

# Function to extract information (dummy example)
def extract_information(file_path):
    # Placeholder for information extraction logic
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
        return data.describe()  # Example: returning a description of the data
    else:
        return None

# Function to validate information (dummy example)
def validate_information(data):
    # Placeholder for validation logic
    return data is not None # Basic validation

# Function to create a certificate (dummy example)
def create_certificate(info):
    # Placeholder for certificate creation logic
    return f"Certificate of Validation: {info}"

# Streamlit interface
st.title("Autoavanza")

st.container()
st.subheader("Clasificación de Documentos")

# Upload zip file
uploaded_file = st.file_uploader("Subir un archivo ZIP que contenga los documentos en PDF", type="zip")

# Custom display order
display_order = [
    "FACTURA",
    "FACTURA REVERSO",
    "INE",
    "INE REVERSO",
    "TARJETA_CIRCULACION",
    "TARJETA_CIRCULACION_REVERSO",
    "REVISAR"
]

if uploaded_file is not None:
    # Decompress files
    directory = decompress_zip(uploaded_file)
    st.success(f"Decompressed files to: {directory}")

    # Store all classified documents as (document_type, filename) pairs
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

    # Sort documents by the defined display order
    sorted_documents = sorted(
        classified_documents,
        key=lambda x: display_order.index(x[0]) if x[0] in display_order else len(display_order)
    )

    # # Display sorted documents
    # for document, filename in sorted_documents:
    #     st.write(f"Archivo: {filename}")
    #     st.write(f"Documento: {document}")

    #     with open(filename, "rb") as pdf_file:
    #         PDFbyte = pdf_file.read()

    #     st.download_button(
    #         label=f"Descargar {document}",
    #         data=PDFbyte,
    #         file_name=document,
    #         key=f"download_{document}_{filename}" 
    #     )

    try:
        st.markdown("## 📄 Documentos Clasificados")

        for i, (document, filename) in enumerate(sorted_documents):
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
                        key=f"download_{document}_{filename}" 
                    )

            # Clean up
            shutil.rmtree(directory)
    except:
        shutil.rmtree(directory)

        # # Extract information
        # info = extract_information(file_path)

        # if validate_information(info):
        #     st.write(f"{file_name} passed validation.")
        #     cert = create_certificate(info)
        #     st.write(cert)
        # else:
        #     st.write(f"{file_name} failed validation.")

# Add any additional Streamlit features here, such as displaying extracted data