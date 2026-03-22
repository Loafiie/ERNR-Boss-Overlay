import re
import cv2
import numpy as np


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

        # Reject extremely long single tokens (true garbage)
        words = text.split()
        if any(len(w) > 40 for w in words):
            return False

        # Must have at least one word with 3+ letters
        if not any(len(w) >= 3 for w in words):
            return False

        letters = re.sub(r'[^A-Za-z]', '', text)
        if not letters:
            return False

        uppercase_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
        if len(text) > 6 and uppercase_ratio > 0.7:
            return False

        # Reject text that's mostly repeated characters (OCR artifact)
        unique_chars = set(text.lower().replace(" ", ""))
        if len(unique_chars) < 3:
            return False

        return True

    @staticmethod
    def preprocess(img):
        """Isolate white/near-white boss name text using HSV color filtering.
        This cleanly removes colored game elements (fire, sky, terrain)
        that brightness-only thresholding cannot distinguish from text."""

        # Resize FIRST so text strokes are thick enough to survive cleanup
        img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_LINEAR)

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # White/near-white text: any hue, low saturation, high brightness
        # This rejects fire (high sat), terrain (high sat), sky (moderate sat)
        lower_white = np.array([0, 0, 170])
        upper_white = np.array([180, 80, 255])
        mask = cv2.inRange(hsv, lower_white, upper_white)

        # Close small gaps in letters, then remove isolated noise dots
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

        # Pad edges — Tesseract is more accurate with whitespace border
        mask = cv2.copyMakeBorder(mask, 20, 20, 20, 20,
                                  cv2.BORDER_CONSTANT, value=0)
        return mask
