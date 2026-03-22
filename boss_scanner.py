import monitor_manager
import mss
import numpy as np
import cv2
import pytesseract
import pyautogui

from ocr_utils import OCRUtils


class BossScanner:
    def __init__(self, regions, tesseract_cmd, config):
        self.regions = regions
        self.region_active = regions
        self.config = config
        self.boss_bar_color = (255, 255, 255)
        self.monitor = monitor_manager.MonitorManager()
        self.is_boss_active()
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def is_boss_active(self) -> bool:
        region_dict = self.monitor.create_boss_bar_region()

        region_boss = (
            region_dict["left"],
            region_dict["top"],
            region_dict["width"],
            region_dict["height"],
        )

        screenshot = pyautogui.screenshot(region=region_boss)
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert to OpenCV BGR

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_color = np.array([0, 120, 70])
        upper_color = np.array([10, 255, 255])

        mask = cv2.inRange(hsv, lower_color, upper_color)

        if cv2.countNonZero(mask) > 0:
            # Find exact coordinates
            y, x = np.where(mask == 255)
            return True
        else:
            print("Bass bar is inactive")
            return False

    def scan_boss_names(self):
        found_names = []

        if self.is_boss_active():
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