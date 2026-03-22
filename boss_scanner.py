import mss
import numpy as np
import cv2
import pytesseract

from ocr_utils import OCRUtils


class BossScanner:
    def __init__(self, regions, tesseract_cmd, config):
        self.regions = regions
        self.config = config
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def scan_boss_names(self):
        found_names = []

        with mss.mss() as sct:
            for i, region in enumerate(self.regions):
                screenshot = sct.grab(region)
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                processed = OCRUtils.preprocess(img)
                text = pytesseract.image_to_string(processed, lang="eng", config=self.config)
                text = OCRUtils.clean_text(text)

                print(f"Region {i}: '{text}'")

                if not OCRUtils.is_valid_ocr_text(text):
                    print(f"Region {i}: rejected as OCR garbage")
                    continue

                found_names.append(text)

        return found_names