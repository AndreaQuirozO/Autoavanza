import pathlib
import Quartz
import Vision
from Cocoa import NSURL
from Foundation import NSDictionary
# needed to capture system-level stderr
from wurlitzer import pipes
import os
from pdf2image import convert_from_path


def image_to_text(img_path, lang="eng"):
    """
    Extracts text from an image file using Apple's Vision framework for OCR.

    This function takes the path to an image file, converts it into a Core Image (CIImage),
    and uses Vision's text recognition capabilities to extract any visible text.

    Parameters:
        img_path (str): The path to the image file to be processed.
        lang (str, optional): The language to use for text recognition. 
                              Currently not used explicitly but can be extended for multi-language support. Default is "eng".

    Returns:
        list of str: A list of recognized text strings found in the image.
    """
    input_url = NSURL.fileURLWithPath_(img_path)

    with pipes() as (out, err):
    # capture stdout and stderr from system calls
    # otherwise, Quartz.CIImage.imageWithContentsOfURL_
    # prints to stderr something like:
    # 2020-09-20 20:55:25.538 python[73042:5650492] Creating client/daemon connection: B8FE995E-3F27-47F4-9FA8-559C615FD774
    # 2020-09-20 20:55:25.652 python[73042:5650492] Got the query meta data reply for: com.apple.MobileAsset.RawCamera.Camera, response: 0
        input_image = Quartz.CIImage.imageWithContentsOfURL_(input_url)

    vision_options = NSDictionary.dictionaryWithDictionary_({})
    vision_handler = Vision.VNImageRequestHandler.alloc().initWithCIImage_options_(
        input_image, vision_options
    )
    results = []
    handler = make_request_handler(results)
    vision_request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handler)
    error = vision_handler.performRequests_error_([vision_request], None)

    return results


def make_request_handler(results):
    """
    Creates a handler function to process OCR results from a Vision text recognition request.

    The returned handler function is designed to be used as the completion callback 
    for a `VNRecognizeTextRequest`. It appends recognized text to the provided `results` list.

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
                # results.append([recognized_text.string(), recognized_text.confidence()])
                results.append(recognized_text.string())
    return handler

def convert_pdf_to_image(pdf_path):
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
    image_path = pdf_path.split('.')[0]+'.jpg'
    images = convert_from_path(pdf_path)
    for count, image in enumerate(images):
        image.save(image_path, 'JPEG')

    return image_path