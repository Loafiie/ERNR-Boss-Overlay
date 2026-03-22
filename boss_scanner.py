import monitor_manager
import mss
import numpy as np
import cv2
import pytesseract
import pyautogui

from ocr_utils import OCRUtils

# Minimum percentage of bright pixels in a region to consider it as containing text
MIN_TEXT_PIXEL_RATIO = 0.003
# Maximum percentage - too many bright pixels means it's not a boss name region
MAX_TEXT_PIXEL_RATIO = 0.40


class BossScanner:
    def __init__(self, regions, tesseract_cmd, config):
        self.regions = regions
        self.config = config
        self.monitor = monitor_manager.MonitorManager()
        self.bar_regions = self.monitor.get_boss_bar_regions()
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def _check_bar(self, bar_region) -> bool:
        """Check if a specific boss health bar is visible (red pixels)."""
        region_tuple = (
            bar_region["left"],
            bar_region["top"],
            bar_region["width"],
            bar_region["height"],
        )

        screenshot = pyautogui.screenshot(region=region_tuple)
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)

        return cv2.countNonZero(mask) > 0

    @staticmethod
    def _region_has_text(img):
        """Check if the region has enough bright pixels to contain text."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
        total = binary.size
        bright = cv2.countNonZero(binary)
        ratio = bright / total
        return MIN_TEXT_PIXEL_RATIO <= ratio <= MAX_TEXT_PIXEL_RATIO

    def scan(self):
        """Scan all regions independently.

        Returns a list (one per region) of dicts:
            {"bar_active": bool, "name": str | None}
        """
        results = []

        with mss.mss() as sct:
            for i, region in enumerate(self.regions):
                bar_active = self._check_bar(self.bar_regions[i])
                name = None

                if bar_active:
                    screenshot = sct.grab(region)
                    img = np.array(screenshot)
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                    if self._region_has_text(img):
                        processed = OCRUtils.preprocess(img)
                        raw = pytesseract.image_to_string(
                            processed, lang="eng", config=self.config
                        )
                        text = OCRUtils.clean_text(raw)

                        if OCRUtils.is_valid_ocr_text(text):
                            name = text

                results.append({"bar_active": bar_active, "name": name})

        return results

