import os

class DocumentClassifier:
    """
    A class to classify documents based on recognized text from OCR output.
    
    This classifier uses a combination of exact phrase matching and keyword-based 
    heuristics to determine the type of document and renames the file accordingly.

    Attributes:
        image_path (str): The original file path of the image/document.
        results (list of str): Text strings extracted from the image (usually OCR output).
        results_set (set): A set of individual uppercase words extracted from results.
        base_name (str): File name without extension.

    Methods:
        classify(): Classifies the document and returns the renamed file path and type.
    """

    def __init__(self, image_path, results):
        """
        Initializes the DocumentClassifier with image path and OCR results.

        Parameters:
            image_path (str): The original file path of the image/document.
            results (list of str): Text strings extracted from the image.
        """
        self.image_path = image_path
        self.results = list(map(str.upper, results))
        self.results_set = set(word for phrase in self.results for word in phrase.split())
        self.base_name, _ = os.path.splitext(self.image_path)

        self.phrase_checks = {
            'CEDO': 'FACTURA REVERSO',
            'FACTURA': 'FACTURA',
            'MÉXICO INSTITUTO NACIONAL ELECTORAL': 'INE',
            'TARJETA DE CIRCULACIÓN VEHICULAR': 'TARJETA CIRCULACION',
            'CODIFICACIONES': 'TARJETA CIRCULACION REVERSO',
        }

        self.keyword_checks = {
            'FACTURA REVERSO': ['CEDO', 'DERECHOS'],
            'FACTURA': ['FACTURA', 'AUTOMOTRIZ', 'EMISOR'],
            'INE': ['ELECTORAL', 'INSTITUTO', 'CREDENCIAL', 'VOTAR'],
            'INE REVERSO': ['INE', 'IDME', 'IDMEX', 'CREDENCIAL', 'VOTAR'],
            'TARJETA CIRCULACION': ['CIRCULACIÓN', 'TARJETA', 'VEHICULO', 'TRANSPORTE', 'GOBIERNO'],
            'TARJETA CIRCULACION REVERSO': ['CODIFICACIONES', 'CACIONES', 'MODALIDAO', 'TRANSPORTE', 'GASOLINA', 'EDOMEX'],
        }

    def classify(self):
        """
        Classifies the document based on the text and renames the file accordingly.

        Returns:
            tuple:
                - new_name (str): The new file name reflecting the identified document type.
                - document (str): The classified document type. Possible values:
                  'FACTURA', 'FACTURA REVERSO', 'INE', 'INE REVERSO', 
                  'TARJETA CIRCULACION', 'TARJETA CIRCULACION_REVERSO', or 'REVISAR'.
        """
        for phrase, doc_type in self.phrase_checks.items():
            if phrase in self.results:
                return self._build_output(doc_type)

        if any(s.startswith('IDMEX') for s in self.results):
            return self._build_output('INE REVERSO')

        for doc_type, keywords in self.keyword_checks.items():
            if any(word in self.results_set or word in self.results for word in keywords):
                return self._build_output(doc_type)

        return self._build_output('REVISAR')

    def _build_output(self, doc_type):
        """
        Constructs the output filename and returns it with the document type.

        Parameters:
            doc_type (str): The identified document type.

        Returns:
            tuple: New file name and document type.
        """
        return f"{self.base_name}_{doc_type}.pdf", doc_type
