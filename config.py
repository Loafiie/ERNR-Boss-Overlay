import os
from resource_path import resource

DB_NAME = resource("bossData.sqlite3")

# In frozen builds Tesseract is bundled; in dev mode use system install
_bundled_tesseract = resource(os.path.join("tesseract", "tesseract.exe"))
if os.path.isfile(_bundled_tesseract):
    TESSERACT_CMD = _bundled_tesseract
    # Tesseract needs TESSDATA_PREFIX to find eng.traineddata
    os.environ["TESSDATA_PREFIX"] = resource(os.path.join("tesseract", "tessdata"))
else:
    TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

OCR_CONFIG = r'--psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ, '
SCAN_INTERVAL = 0.25
