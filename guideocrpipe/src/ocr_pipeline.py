import pytesseract
from PIL import Image
import cv2
import numpy as np
from pathlib import Path
import logging

class OCRPipeline:
    def __init__(self, tesseract_path=None):
        """
        Initialize the OCR pipeline
        :param tesseract_path: Path to tesseract executable (needed for Windows)
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        self.logger = logging.getLogger(__name__)
        self._configure_logging()

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