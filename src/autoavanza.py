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
import urllib3
from selenium.common.exceptions import WebDriverException
from dateutil.parser import parse


from OCR import TextExtractor
from DocumentClassification import DocumentClassifier
from Staging import Staging
from QRExctraction import CFDIValidator
from DataExtraction import INEDataExtractor, FacturaDataExtractor, FacturaReversoDataExtractor, TarjetCirculacionDataExtractor
from DataValidation import DataValidator
from SignatureStampValidation import SignatureStampValidator
from Ruling import RulingMaker

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

documents_revised = [
                    "FACTURA",
                    "FACTURA REVERSO",
                    "INE",
                    "INE REVERSO",
                    "TARJETA CIRCULACION",
                    "TARJETA CIRCULACION REVERSO",
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
                    data_extractor = TextExtractor()
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

def check_fecha_if_tipo_applies(data):
    tipo = data.get("Tipo de fecha de vigencia", "")
    
    if isinstance(tipo, str) and tipo.strip().lower().endswith("fecha"):
        fecha = data.get("Valor de fecha de vigencia")
        if not isinstance(fecha, str):
            return False
        try:
            parse(fecha, dayfirst=True, fuzzy=False)
        except (ValueError, TypeError):
            return False
        
def check_fecha_if_tipo_applies_periodo(data):
    tipo = data.get("Tipo de fecha de vigencia", "")
    if isinstance(tipo, str) and (tipo.strip().lower().endswith("periodo")):
        periodo = data.get("Valor de fecha de vigencia")
        try:
            int(periodo)
        except (ValueError, TypeError):
            return False

    return True

def check_fecha_expedicion(data):

    tipo = data.get("Tipo de fecha de vigencia", "")
    
    if isinstance(tipo, str) and (tipo.strip().lower().endswith("periodo") or tipo.strip().lower().endswith("permanente")):
        return True
    elif isinstance(tipo, str) and tipo.strip().lower().endswith("fecha"):
        fecha = data.get("Valor de fecha de expedicion")
        if not isinstance(fecha, str):
            return False
        try:
            parse(fecha, dayfirst=True, fuzzy=False)
        except (ValueError, TypeError):
            return False

    return True


def all_values_valid(data):
    """
    Recursively checks that all values in the dictionary (and nested dictionaries)
    are not equal to 'N/A'.
    """
    if isinstance(data, dict):
        for value in data.values():
            if not all_values_valid(value):
                return False
    elif isinstance(data, list):
        for item in data:
            if not all_values_valid(item):
                return False
    else:
        if data == 'N/A':
            return False
    return True


def display_single_value_with_edit(document_name, field_key, extracted_value):
    data = st.session_state.get(document_name, {})
    if extracted_value == 'N/A':
        updated_val = st.text_input(f"❗️❗️{field_key}❗️❗️", value=extracted_value, key=f"{document_name}_{field_key}")
    else:
        updated_val = st.text_input(f"{field_key}", value=extracted_value, key=f"{document_name}_{field_key}")
    # Save back just this single value (keep other fields if present)
    updated_data = data.copy()
    updated_data[field_key] = updated_val
    st.session_state[document_name] = updated_data

def display_single_value_with_dropdown(document_name, field_key, extracted_value, options):
    data = st.session_state.get(document_name, {})
    default_val = data.get(field_key, extracted_value)
    updated_val = st.selectbox(
        f"{field_key}",
        options=options,
        index=options.index(default_val) if default_val in options else 0,
        key=f"{document_name}_{field_key}"
    )
    # Save back just this single value (keep other fields if present)
    updated_data = data.copy()
    updated_data[field_key] = updated_val
    st.session_state[document_name] = updated_data

def has_revisar_type(data_dict):
    for file_info in data_dict.values(): # Iterate over the nested dictionaries
        # Use .get('type') to safely access the 'type' key,
        # in case an entry somehow doesn't have it.
        if file_info.get('type') == 'REVISAR':
            return True  # Found 'REVISAR'
    return False # No 'REVISAR' found after checking all entries



# ---------------------------  Streamlit interface begins  --------------------------- #
logo = Image.open(logo_path)
st.set_page_config( page_title='Autoavanza', page_icon=logo)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(logo_path)  # Adjust width as needed

st.container()
st.markdown("## Carga de Documentos")

# ---------------------------  Upload and decompress ZIP  --------------------------- #
uploaded_file = st.file_uploader("Subir un archivo ZIP que contenga los documentos en PDF", type="zip")

if uploaded_file is not None:
    file_hash = get_file_hash(uploaded_file)

    if st.session_state.get("last_file_hash") != file_hash:
        st.session_state.last_file_hash = file_hash
        directory = decompress_zip(uploaded_file)
        st.success(f"Archivos decomprimidos correctamente")

        # ---------------------------  Classify documents  --------------------------- #

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

        if not has_revisar_type(st.session_state.classified_documents_data):
            if st.button("✅ Apruebo clasificación, continuar con extracción de datos", key="aprobacion_clasificacion"):
                factura_file = None
                document_files = {}

                for doc_info in st.session_state.classified_documents_data.values():
                    doc_type = doc_info["type"]
                    filename = doc_info["filename"]
                    text = doc_info["text"]

                    if doc_type in documents_revised:
                        document_files[doc_type] = {"filename": filename, "text": text}

                    factura_file = document_files.get("FACTURA", {}).get("filename")
                    factura_text = document_files.get("FACTURA", {}).get("text")

                    factura_reverso_file = document_files.get("FACTURA REVERSO", {}).get("filename")
                    factura_reverso_text = document_files.get("FACTURA REVERSO", {}).get("text")

                    ine_file = document_files.get("INE", {}).get("filename")
                    ine_text = document_files.get("INE", {}).get("text")

                    ine_reverso_file = document_files.get("INE REVERSO", {}).get("filename")
                    ine_reverso_text = document_files.get("INE REVERSO", {}).get("text")

                    tarjeta_circulacion_file = document_files.get("TARJETA CIRCULACION", {}).get("filename")
                    tarjeta_circulacion_text = document_files.get("TARJETA CIRCULACION", {}).get("text")

                    tarjeta_circulacion_reverso_file = document_files.get("TARJETA CIRCULACION REVERSO", {}).get("filename")
                    tarjeta_circulacion_reverso_text = document_files.get("TARJETA CIRCULACION REVERSO", {}).get("text")

                datos_factura = None
                datos_factura_SAT = None
                datos_factura_reverso = None
                datos_ine = None
                datos_tarjeta = None


                if factura_file and os.path.exists(factura_file):
                    input_message = '\n'.join(factura_text)
                    factura_data_extractor = FacturaDataExtractor(input_message, GEMINI_API_KEY)
                    st.session_state.datos_factura = factura_data_extractor.extraer_datos()

                else:
                    st.error("⚠️ No se encontró ningún archivo clasificado como FACTURA.")

                
                if factura_reverso_file and os.path.exists(factura_reverso_file):
                    input_message = '\n'.join(factura_reverso_text)
                    factura_data_extractor = FacturaReversoDataExtractor(input_message, GEMINI_API_KEY)
                    st.session_state.datos_factura_reverso = factura_data_extractor.extraer_datos()
                else:
                    st.error("⚠️ No se encontró ningún archivo clasificado como FACTURA REVERSO.")

                
                if ine_file and os.path.exists(ine_file):
                    input_message = '\n'.join(ine_text)
                    ine_data_extractor = INEDataExtractor(input_message, GEMINI_API_KEY)
                    st.session_state.datos_ine = ine_data_extractor.extraer_datos()
                else:
                    st.error("⚠️ No se encontró ningún archivo clasificado como INE.")

                
                if tarjeta_circulacion_file and os.path.exists(tarjeta_circulacion_file):
                    input_message = '\n'.join(tarjeta_circulacion_text)
                    tarjeta_data_extractor = TarjetCirculacionDataExtractor(input_message, GEMINI_API_KEY)
                    st.session_state.datos_tarjeta = tarjeta_data_extractor.extraer_datos()
                else:
                    st.error("⚠️ No se encontró ningún archivo clasificado como TARJETA CIRCULACION.")


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
                    st.session_state.mostrar_datos = True
        else:
            st.warning("⚠️ Algunos documentos aún no han sido clasificados. Revísalos para continuar.")



    if "validator" in st.session_state and "captcha_path" in st.session_state:
        with st.form(key="captcha_form"):
            st.image(st.session_state.captcha_path, caption="Ingrese el código CAPTCHA")
            
            input_key = f"captcha_input_{st.session_state.captcha_attempts}"
            user_code = st.text_input("Código CAPTCHA", key=input_key)

            if st.form_submit_button("🔐 Validar Código"):
                try:
                    st.session_state.captcha_attempts += 1
                    datos_factura_SAT = st.session_state.validator.extract_data_with_code(user_code)

                    if datos_factura_SAT:
                        st.success("✅ Datos extraídos correctamente del SAT")
                        st.session_state.datos_factura_SAT = datos_factura_SAT  # Save SAT data
                        st.session_state.mostrar_datos = True

                        # Clean up session state
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

                except (urllib3.exceptions.MaxRetryError, WebDriverException, ConnectionRefusedError) as e:
                    st.error("❌ Error al conectar con el navegador. Intenta reiniciar el proceso.")

                    if "validator" in st.session_state:
                        try:
                            st.session_state.validator.close_browser()
                        except:
                            pass

                    for key in ["captcha_attempts", "validator", "captcha_path"]:
                        if key in st.session_state:
                            del st.session_state[key]


    if st.session_state.get("mostrar_datos", False):
        st.markdown("## Datos Extraídos")

        if "datos_factura" in st.session_state:
            st.subheader("📄 Datos de la Factura")
            for key, value in st.session_state.datos_factura.items():
                display_single_value_with_edit("datos_factura", key, value)
                # st.write(f"**{key}**: {value}")

        if "datos_factura_SAT" in st.session_state:
            st.subheader("📄 Datos del SAT")
            for key, value in st.session_state.datos_factura_SAT.items():
                display_single_value_with_edit("datos_factura_SAT", key, value)
                # st.write(f"**{key}**: {value}")

        if "datos_factura_reverso" in st.session_state and st.session_state.datos_factura_reverso is not None:
            st.subheader("📄 Datos del Reverso de la Factura")
            for key, value in st.session_state.datos_factura_reverso.items():
                display_single_value_with_edit("datos_factura_reverso", key, value)
                # st.write(f"**{key}**: {value}")

        if "datos_ine" in st.session_state:
            st.subheader("🪪 Datos del INE")
            for key, value in st.session_state.datos_ine.items():
                display_single_value_with_edit("datos_ine", key, value)
                # st.write(f"**{key}**: {value}")

        if "datos_tarjeta" in st.session_state and st.session_state.datos_tarjeta is not None:
            st.subheader("🚗 Datos de la Tarjeta de Circulación")
            for key, value in st.session_state.datos_tarjeta.items():
                if key == "Tipo de fecha de vigencia":
                    display_single_value_with_dropdown("datos_tarjeta", key, value, ["fecha", "periodo", "permanente"])
                else:
                    display_single_value_with_edit("datos_tarjeta", key, value)
                # st.write(f"**{key}**: {value}")

        
        all_data_keys = ["datos_factura", "datos_factura_SAT", "datos_factura_reverso", "datos_ine", "datos_tarjeta"]

        for key in all_data_keys:
            if key not in st.session_state:
                st.session_state[key] = None


        data_is_complete = all(
            all_values_valid(st.session_state.get(key, {}))
            for key in all_data_keys
        )


        if data_is_complete:
            if check_fecha_if_tipo_applies(st.session_state.datos_tarjeta) or check_fecha_if_tipo_applies_periodo(st.session_state.datos_tarjeta):
                if check_fecha_expedicion(st.session_state.datos_tarjeta) or True:
                    if 'datos_aprobados' not in st.session_state:
                        st.session_state.datos_aprobados = False

                    if st.button("✅ Apruebo datos, continuar con validación"):
                        st.session_state.datos_aprobados = True

                    if st.session_state.datos_aprobados:

                        data_validator = DataValidator(datos_factura=st.session_state.datos_factura,
                                                    datos_factura_SAT=st.session_state.datos_factura_SAT, 
                                                    datos_factura_reverso=st.session_state.datos_factura_reverso, 
                                                    datos_ine=st.session_state.datos_ine, 
                                                    datos_tarjeta=st.session_state.datos_tarjeta

                            )
                        
                        data_results_bool, data_results_message = data_validator.data_validator_pipeline()

                        st.markdown("## Resultados de la validación")
                        for (k_b, v_b), (k_m, v_m) in zip(data_results_bool.items(), data_results_message.items()):
                            if isinstance(v_m, dict):
                                estado = v_m.get("Estado", "")
                                detalles = v_m.get("detalles", {})
                                detalle_lines = "\n".join([f"- **{k}**: {v}" for k, v in detalles.items()])
                                formatted_message = f"{estado}\n\n{detalle_lines}"
                            else:
                                formatted_message = v_m

                            if k_b == 'validacion_adeudos':
                                st.warning(f"⚠️ {formatted_message}")
                            elif v_b:
                                st.success(f"✅  {formatted_message}")
                            else:
                                st.error(f"❌  {formatted_message}")

                        if 'validar_firmas_sellos' not in st.session_state:
                            st.session_state.validar_firmas_sellos = False

                        if st.button("✅ Apruebo validación de datos, continuar con validación de firmas y sellos"):
                            st.session_state.validar_firmas_sellos = True

                        if st.session_state.validar_firmas_sellos:

                            by_type = {doc["type"]: doc["filename"] for doc in st.session_state.classified_documents_data.values()}

                            factura_reverso_path = by_type.get("FACTURA REVERSO")
                            ine_path = by_type.get("INE")
                            tarjeta_path = by_type.get("TARJETA CIRCULACION")

                            model_path = os.path.join(os.path.dirname(__file__), 'models', 'best.pt')
                            sig_val = SignatureStampValidator(model_path, ine_path, factura_reverso_path, tarjeta_path)

                            sign_results_bool, sign_results_message, sign_results_path = sig_val.signature_stamp_validator_pipeline()
                            
                            st.markdown("## Resultados de la validación")
                            for (k_b, v_b), (k_m, v_m) in zip(sign_results_bool.items(), sign_results_message.items()):
                                formatted_message = v_m

                                if v_b:
                                    st.success(f"✅  {formatted_message}")
                                else:
                                    st.error(f"❌  {formatted_message}")

                                ine_save_path = sign_results_path.get("validacion_firma_ine_factura_ine_path")
                                factura_save_path = sign_results_path.get("validacion_firma_ine_factura_factura_path")
                                tarjeta_save_path = sign_results_path.get("validacion_firma_ine_tarjeta_tarjeta_path")
                                if k_b == 'validacion_firma_ine_factura' and ine_save_path and factura_save_path:

                                    col1, col2 = st.columns(2)

                                    with col1:
                                        st.image(ine_save_path, caption="Firma de INE", width=300)

                                    with col2:
                                        st.image(factura_save_path, caption="Firma de Factura", width=300)

                                    st.session_state.agree_validation_ine_factura = st.checkbox("Rechazo el resultado de la comparación automática de firmas")
                                    
                                    if st.session_state.agree_validation_ine_factura:
                                        if v_b:
                                            sign_results_bool[k_b] = False
                                            sign_results_message[k_b] = 'Se requiere que el solicitante vuelva a firmar lo más parecido posible ya que no coincide firma en INE y Reverso de Factura'
                                        else:
                                            sign_results_bool[k_b] = True
                                            sign_results_message[k_b] = 'Firma de INE coincide con Reverso de Factura'
        


                                elif k_b == 'validacion_firma_ine_tarjeta' and ine_save_path and tarjeta_save_path:
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.image(ine_save_path, caption="Firma de INE", width=300)

                                    with col2:
                                        st.image(tarjeta_save_path, caption="Firma de Tarjeta", width=300)

                                    st.session_state.agree_validation_ine_tarjeta = st.checkbox("Rechazo el resultado de la comparación automática de firmas")
                                    
                                    if st.session_state.agree_validation_ine_tarjeta:
                                        if v_b:
                                            sign_results_bool[k_b] = False
                                            sign_results_message[k_b] = "Se solicita corrección - en 24hrs. Se rechaza por discrepancia en firma de INE y Tarjeta de Circulación"
                                        else:
                                            sign_results_bool[k_b] = True
                                            sign_results_message[k_b] = "Firma de INE coincide con Tarjeta de Circualción"

                                if v_m == 'No se encontró firma en Tarjeta de Circulación':
                                    agree_falta_firma_tarjeta = st.checkbox("Confirmo que no hay firma en tarjeta de circulación")
                                    if agree_falta_firma_tarjeta:
                                        sign_results_bool[k_b] = True
                                        sign_results_message[k_b] = "Esta tarjeta de circulación no cuenta con firma"
                                    else:
                                        sign_results_bool[k_b] = False
                                        sign_results_message[k_b] = "La detección automática de firmas no encontró firma en Tarjeta de Circulación, pero el usuario confirma que sí hay firma. Se recomienda intervención manual para checar firmas en Tarjeta de Circulación y Reverso de Factura"
                                
                            if 'aprobado_firmas_sellos' not in st.session_state:
                                st.session_state.aprobado_firmas_sellos = False
                            
                            if st.button("✅ Apruebo validación de firmas, continuar con certamen"):
                                st.session_state.aprobado_firmas_sellos = True

                            if st.session_state.aprobado_firmas_sellos:
                                ruler = RulingMaker(data_results_message, data_results_bool, sign_results_message, sign_results_bool, GEMINI_API_KEY)


                                if "response" not in st.session_state:
                                    ruler = RulingMaker(data_results_message, data_results_bool, sign_results_message, sign_results_bool, GEMINI_API_KEY)
                                    st.session_state.response = ruler.obtener_dictamen()  # Only call once!

                                pdf_path = ruler.generar_pdf_dictamen()

                                st.markdown("## Dictámen")

                                df_total = ruler.return_table_dictamen()
                                st.dataframe(df_total, use_container_width=True, hide_index=True, row_height=70)


                                st.write(st.session_state.response)

                                with open(pdf_path, "rb") as f:
                                    st.download_button("Descargar Dictamen en PDF", f, file_name="dictamen_validacion.pdf", mime="application/pdf")

                else:
                    st.warning("⚠️ El campo de Fecha de expedición de la Tarjeta de Circulación tiene formato incorrecto. Por favor, corrígelo antes de continuar.")

            else:
                # st.warning("⚠️ Algunos campos de fecha tienen formatos incorrectos. Por favor, corrígelos antes de continuar.")
                st.warning("⚠️ El campo de Fecha de vigencia de la Tarjeta de Circulación tiene formato incorrecto. Por favor, corrígelo antes de continuar.")
        else:
            st.warning("⚠️ Algunos campos están incompletos (N/A). Complétalos para continuar.")
            