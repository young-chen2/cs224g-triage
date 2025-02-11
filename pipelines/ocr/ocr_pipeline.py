import pytesseract
from PIL import Image
import cv2
import numpy as np
from pathlib import Path
import logging
import google.generativeai as genai
from PIL import Image
import os
from pdf2image import convert_from_path
import logging
from typing import List, Optional

class GeminiOCRHandler:
    def __init__(self, api_key):
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY', api_key))
        self.model = genai.GenerativeModel('gemini-pro-vision')
        self.logger = logging.getLogger(__name__)

    def process_pdf(self, pdf_path):
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            extracted_text = []
            
            for i, image in enumerate(images):
                self.logger.info(f"Processing page {i+1}")
                # Get text from image using Gemini
                response = self.model.generate_content(image)
                extracted_text.append(response.text)
            
            return "\n".join(extracted_text)
            
        except Exception as e:
            self.logger.error(f"Error processing PDF: {str(e)}")
            return None

    def process_image(self, image_path):
        try:
            image = Image.open(image_path)
            response = self.model.generate_content(image)
            return response.text
        except Exception as e:
            self.logger.error(f"Error processing image: {str(e)}")
            return None 

class OCRPipeline:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key is required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')
        self.logger = logging.getLogger(__name__)

    def process_pdf(self, pdf_path: str) -> str:
        """Process a PDF file and extract text using Gemini Vision API"""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            extracted_text = []
            
            for i, image in enumerate(images):
                self.logger.info(f"Processing page {i+1} of PDF")
                response = self.model.generate_content(image)
                extracted_text.append(response.text)
            
            return "\n".join(extracted_text)
            
        except Exception as e:
            self.logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise

    def process_image(self, image_path: str) -> str:
        """Process a single image and extract text using Gemini Vision API"""
        try:
            image = Image.open(image_path)
            response = self.model.generate_content(image)
            return response.text
        except Exception as e:
            self.logger.error(f"Error processing image {image_path}: {str(e)}")
            raise

    def process_directory(self, dir_path: str) -> dict:
        """Process all PDFs and images in a directory"""
        results = {}
        dir_path = Path(dir_path)
        
        for file_path in dir_path.glob("**/*"):
            if file_path.suffix.lower() in ['.pdf']:
                try:
                    results[str(file_path)] = self.process_pdf(str(file_path))
                except Exception as e:
                    self.logger.error(f"Failed to process {file_path}: {str(e)}")
                    results[str(file_path)] = None
            elif file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                try:
                    results[str(file_path)] = self.process_image(str(file_path))
                except Exception as e:
                    self.logger.error(f"Failed to process {file_path}: {str(e)}")
                    results[str(file_path)] = None
                    
        return results

    def _configure_logging(self):
        """Configure basic logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def preprocess_image(self, image):
        """
        Preprocess the image for better OCR results
        :param image: Input image (numpy array or PIL Image)
        :return: Preprocessed image
        """
        if isinstance(image, Image.Image):
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to preprocess the image
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # Apply dilation to connect text components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        gray = cv2.dilate(gray, kernel, iterations=1)

        # Apply median blur to remove noise
        gray = cv2.medianBlur(gray, 3)

        return gray

    def extract_text(self, image_path, lang='eng'):
        """
        Extract text from an image file
        :param image_path: Path to the image file
        :param lang: Language for OCR (default: 'eng')
        :return: Extracted text and structured data
        """
        try:
            # Read the image
            image_path = Path(image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")

            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")

            # Preprocess the image
            processed_image = self.preprocess_image(image)

            # Perform OCR
            self.logger.info(f"Performing OCR on {image_path}")
            text = pytesseract.image_to_string(processed_image, lang=lang)
            
            # Process the extracted text through the interpreter
            interpreter = GuidelineInterpreter()
            structured_data = interpreter.process_text(text.strip())
            
            return {
                'raw_text': text.strip(),
                'structured_data': structured_data
            }

        except Exception as e:
            self.logger.error(f"Error processing {image_path}: {str(e)}")
            raise 