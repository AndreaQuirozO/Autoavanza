import os
import pathlib
import Quartz
import Vision
from Cocoa import NSURL
from Foundation import NSDictionary
from wurlitzer import pipes
from pdf2image import convert_from_path

class DataExtractor:
    """
    A class to process PDF and image documents using Apple's Vision framework and pdf2image.

    Provides utilities to:
      - Convert PDFs to images.
      - Extract text from images via OCR.
    """

    def __init__(self, lang="eng"):
        """
        Initializes the DocumentProcessor.

        Parameters:
            lang (str): Language used for text recognition (currently unused, for future extension).
        """
        self.lang = lang

    def convert_pdf_to_image(self, pdf_path):
        """
        Converts the first page of a PDF file to a JPEG image.

        Parameters:
            pdf_path (str): The file path to the input PDF.

        Returns:
            str: The file path to the saved JPEG image.

        Notes:
            - Only the first page of the PDF is saved as an image.
            - The output image is saved with the same base name as the PDF, but with a .jpg extension.
        """
        self.image_path = pdf_path.split('.')[0] + '.jpg'
        images = convert_from_path(pdf_path)
        for count, image in enumerate(images):
            image.save(self.image_path, 'JPEG')
        return self.image_path

    def image_to_text(self, img_path):
        """
        Extracts text from an image file using Apple's Vision framework for OCR.

        Parameters:
            img_path (str): The path to the image file to be processed.

        Returns:
            list of str: A list of recognized text strings found in the image.
        """
        input_url = NSURL.fileURLWithPath_(img_path)

        with pipes() as (out, err):
            input_image = Quartz.CIImage.imageWithContentsOfURL_(input_url)

        vision_options = NSDictionary.dictionaryWithDictionary_({})
        vision_handler = Vision.VNImageRequestHandler.alloc().initWithCIImage_options_(
            input_image, vision_options
        )
        results = []
        handler = self._make_request_handler(results)
        vision_request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handler)
        error = vision_handler.performRequests_error_([vision_request], None)

        return results

    def _make_request_handler(self, results):
        """
        Creates a handler function to process OCR results from a Vision text recognition request.

        Parameters:
            results (list): A list that will be populated with recognized text strings.

        Returns:
            function: A handler function that takes `request` and `error` as parameters.

        Raises:
            ValueError: If `results` is not a list.
        """
        if not isinstance(results, list):
            raise ValueError("results must be a list")

        def handler(request, error):
            if error:
                print(f"Error! {error}")
            else:
                observations = request.results()
                for text_observation in observations:
                    recognized_text = text_observation.topCandidates_(1)[0]
                    results.append(recognized_text.string())
        return handler
    

    def delete_image(self):
        """
        Deletes the image file created during PDF conversion.

        Raises:
            FileNotFoundError: If the image file does not exist.
        """
        if os.path.exists(self.image_path):
            os.remove(self.image_path)
        else:
            raise FileNotFoundError(f"The file {self.image_path} does not exist.")
