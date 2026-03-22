import time

from config import DB_NAME, TESSERACT_CMD, OCR_CONFIG, SCAN_INTERVAL
from monitor_manager import MonitorManager
from boss_scanner import BossScanner
from boss_database import BossDatabase


class BossApp:
    def __init__(self):
        monitor_manager = MonitorManager()
        regions = monitor_manager.get_regions()

        self.scanner = BossScanner(
            regions=regions,
            tesseract_cmd=TESSERACT_CMD,
            config=OCR_CONFIG
        )
        self.database = BossDatabase(DB_NAME)

    def print_match(self, match):
        print(
            match["boss_name"],
            match["standard"],
            match["slash"],
            match["strike"],
            match["pierce"],
            match["magic"],
            match["fire"],
            match["lightning"],
            match["holy"],
            match["poison"],
            match["scarlet_rot"],
            match["blood_loss"],
            match["frostbite"],
            match["sleep"],
            match["madness"],
        )

    def run(self):
        while True:
            boss_names = self.scanner.scan_boss_names()
            matches = self.database.find_best_matches(boss_names)

            for match in matches:
                self.print_match(match)

            time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    app = BossApp()
    app.run()