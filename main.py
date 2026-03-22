from config import DB_NAME, TESSERACT_CMD, OCR_CONFIG, SCAN_INTERVAL
from monitor_manager import MonitorManager
from boss_scanner import BossScanner
from boss_database import BossDatabase
from overlay import create_overlay, build_rows, Window


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

        self.overlay = create_overlay(x=75, y=175, w=300, h=180)
        self.last_boss_name = None

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

    def update_overlay(self, match):
        left_rows, right_rows = build_rows(
            match["standard"],
            match["slash"],
            match["strike"],
            match["pierce"],
            match["magic"],
            match["fire"],
            match["lightning"],
            match["holy"],
        )

        self.overlay.set_overlay(
            match["boss_name"],
            left_rows,
            right_rows
        )

    def scan_once(self):
        boss_names = self.scanner.scan_boss_names()
        matches = self.database.find_best_matches(boss_names)

        if matches:
            #foreach match generate overlay with offset to the right
            #recheck if something has changed
                #if it did redraw the overlay
                #if not do nothing

            match = matches[0]
            self.print_match(match)

            if match["boss_name"] != self.last_boss_name:
                self.last_boss_name = match["boss_name"]

            self.update_overlay(match)

        Window.after(int(SCAN_INTERVAL * 1000), self.scan_once)

    def run(self):
        Window.after(100, self.scan_once)
        Window.launch()


if __name__ == "__main__":
    app = BossApp()
    app.run()