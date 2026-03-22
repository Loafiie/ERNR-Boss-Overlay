import re
import cv2


class OCRUtils:
    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r'[^a-zA-Z ]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def normalize_text(text: str) -> str:
        return re.sub(r'[^a-z]', '', text.lower())

    @staticmethod
    def is_valid_ocr_text(text: str) -> bool:
        text = OCRUtils.clean_text(text)

        if not text:
            return False

        if len(text) < 4:
            return False

        if " " not in text and len(text) > 12:
            return False

        letters = re.sub(r'[^A-Za-z]', '', text)
        if not letters:
            return False

        uppercase_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
        if len(text) > 10 and uppercase_ratio > 0.8:
            return False

        return True

    @staticmethod
    def preprocess(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.convertScaleAbs(gray, alpha=2.5, beta=-120)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        _, gray = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)
        gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_LINEAR)
        return gray