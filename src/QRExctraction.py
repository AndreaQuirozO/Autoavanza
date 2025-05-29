from pdf2image import convert_from_path
from PIL import Image
import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import time
from Staging import Staging

class CFDIValidator:
    """
    Class for validating electronic invoices (CFDIs) by extracting and processing
    a QR code contained in a PDF file, followed by an online validation
    that requires manual CAPTCHA input.

    Attributes:
        pdf_path (str): Path to the invoice PDF file.
        image_path (str): Path to the image generated from the PDF.
        browser (webdriver.Chrome): Selenium-controlled Chrome browser instance.
    """

    def __init__(self, pdf_path):
        """
        Initializes the CFDIValidator with the given PDF file.

        Args:
            pdf_path (str): Path to the PDF file containing the CFDI.
        """
        self.pdf_path = pdf_path
        self.image_path = self.convert_pdf_to_image()
        self.browser = None

    def convert_pdf_to_image(self):
        """
        Converts the first page of the PDF to a PNG image.

        Returns:
            str: Path to the generated image file.
        """
        image_path = self.pdf_path.split('.')[0] + '.png'
        images = convert_from_path(self.pdf_path)
        images[0].save(image_path, 'PNG')
        return image_path

    def extract_url_from_qr(self):
        """
        Extracts valid URLs from a QR code found in the image,
        specifically checking for SAT verification links.

        Returns:
            list: List of SAT verification URLs extracted from the QR code.
        """
        image = cv2.imread(self.image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        qr_codes = decode(gray, symbols=[ZBarSymbol.QRCODE])

        sat_base_url = "https://verificacfdi.facturaelectronica.sat.gob.mx"
        urls = []

        for qr_code in qr_codes:
            data = qr_code.data.decode('utf-8')
            if data.startswith(sat_base_url):
                urls.append(data)

        os.remove(self.image_path)  # Delete image after processing
        return urls


    def open_browser(self, url):
        """
        Opens a headless Chrome browser and navigates to the provided URL.

        Args:
            url (str): URL extracted from the QR code.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # run in headless mode
        chrome_options.add_argument("--disable-gpu")  # recommended for headless
        chrome_options.add_argument("--no-sandbox")  # avoid some container issues
        chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
        chrome_options.add_argument("--window-size=1920,1080")  # ensure full viewport

        self.browser = webdriver.Chrome(options=chrome_options)
        # self.browser = webdriver.Chrome()
        self.browser.get(url)

    def save_captcha_image_for_streamlit(self):
        """
        Saves the CAPTCHA image to a temporary path for Streamlit display.

        Returns:
            str: Path to the saved CAPTCHA image.
        """
        captcha_img = self.browser.find_element(By.CLASS_NAME, 'captchaimage')

        self.staging_captcha = Staging("captchas")
        self.staging_captcha_path = self.staging_captcha.run()

        captcha_path = os.path.join(self.staging_captcha_path, 'captcha.png')
        captcha_img.screenshot(captcha_path)
        return captcha_path
    

    def send_captcha_code(self, code):
        """
        Sends the CAPTCHA code to the website.
        """
        self.browser.find_element(By.ID, 'ctl00_MainContent_TxtCaptchaNumbers').clear()
        self.browser.find_element(By.ID, 'ctl00_MainContent_TxtCaptchaNumbers').send_keys(code)
        self.browser.find_element(By.XPATH, '//*[@id="ctl00_MainContent_BtnBusqueda"]').click()


    # def refresh_captcha_image(self):
    #     """
    #     Refresca la imagen del CAPTCHA y la guarda.
    #     """
    #     time.sleep(1)  # Dale chance al navegador de cargar el nuevo CAPTCHA
    #     captcha_img = self.browser.find_element(By.CLASS_NAME, 'captchaimage')
    #     captcha_path = os.path.join(self.staging_captcha_path, 'captcha.png')

    #     # Elimina la anterior si existe
    #     if os.path.exists(captcha_path):
    #         os.remove(captcha_path)

    #     captcha_img.screenshot(captcha_path)
    #     return captcha_path



    def extract_data_with_code(self, code):
        """
        Attempts to extract data after sending CAPTCHA.

        Returns:
            dict or None: Extracted data or None if not found.
        """
        self.send_captcha_code(code)
        try:
            WebDriverWait(self.browser, 5).until(
                EC.presence_of_element_located((By.ID, 'ctl00_MainContent_LblNombreReceptor'))
            )
            data = {
                "Nombre Receptor": self.browser.find_element(By.ID, 'ctl00_MainContent_LblNombreReceptor').text,
                "Nombre Emisor": self.browser.find_element(By.ID, 'ctl00_MainContent_LblNombreEmisor').text,
                "RFC Receptor": self.browser.find_element(By.ID, 'ctl00_MainContent_LblRfcReceptor').text,
                "RFC Emisor": self.browser.find_element(By.ID, 'ctl00_MainContent_LblRfcEmisor').text,
                "Fecha Certificación": self.browser.find_element(By.ID, 'ctl00_MainContent_LblFechaCertificacion').text,
                "Fecha Expedición": self.browser.find_element(By.ID, 'ctl00_MainContent_LblFechaEmision').text,
                "Folio Fiscal": self.browser.find_element(By.ID, 'ctl00_MainContent_LblUuid').text,
                "Total": self.browser.find_element(By.ID, 'ctl00_MainContent_LblMonto').text,
                "Estado CDFI": self.browser.find_element(By.ID, 'ctl00_MainContent_LblEstado').text
            }
            self.browser.quit()
            return data
        except:
            return None


    def close_browser(self):
        """
        Closes the browser if it's currently open.
        """
        if self.browser:
            self.browser.quit()
            self.browser = None


