import os
def classify_document(results, image_path):
    """
    Classifies a document based on recognized text and returns a renamed file path and document type.

    Parameters:
        results (list of str): A list of text strings extracted from an image (usually OCR output).
        image_path (str): The original file path of the image/document.

    Returns:
        tuple:
            - new_name (str): The modified file name reflecting the identified document type.
            - document (str): The classified document type. Possible values include:
                'FACTURA', 'FACTURA_REVERSO', 'INE', 'INE_REVERSO', 
                'TARJETA_CIRCULACION', 'TARJETA_CIRCULACION_REVERSO', or 'REVISAR' if unclassified.
    """
    results = list(map(str.upper, results))
    results_set = set(word for phrase in results for word in phrase.split())

    base_name, _ = os.path.splitext(image_path)

    # Exact phrase-based rules
    phrase_checks = {
        'CEDO': 'FACTURA_REVERSO',
        'FACTURA': 'FACTURA',
        'MÉXICO INSTITUTO NACIONAL ELECTORAL': 'INE',
        'TARJETA DE CIRCULACIÓN VEHICULAR': 'TARJETA_CIRCULACION',
        'CODIFICACIONES': 'TARJETA_CIRCULACION_REVERSO',
    }

    for phrase, doc_type in phrase_checks.items():
        if phrase in results:
            return f"{base_name}_{doc_type}.pdf", doc_type

    # Prefix and keyword-based rules
    if any(s.startswith('IDMEX') for s in results):
        return f"{base_name}_INE_REVERSO.pdf", 'INE_REVERSO'

    keyword_checks = {
        'FACTURA_REVERSO': ['CEDO', 'DERECHOS'],
        'FACTURA': ['FACTURA', 'AUTOMOTRIZ', 'EMISOR'],
        'INE': ['ELECTORAL', 'INSTITUTO', 'CREDENCIAL', 'VOTAR'],
        'INE_REVERSO': ['INE', 'IDME', 'IDMEX', 'CREDENCIAL', 'VOTAR'],
        'TARJETA_CIRCULACION': ['CIRCULACIÓN', 'TARJETA', 'VEHICULO', 'TRANSPORTE', 'GOBIERNO'],
        'TARJETA_CIRCULACION_REVERSO': ['CODIFICACIONES', 'CACIONES', 'MODALIDAO', 'TRANSPORTE', 'GASOLINA', 'EDOMEX'],
    }

    for doc_type, keywords in keyword_checks.items():
        if any(word in results_set or word in results for word in keywords):
            return f"{base_name}_{doc_type}.pdf", doc_type

    return f"{base_name}_REVISAR.pdf", 'REVISAR'
