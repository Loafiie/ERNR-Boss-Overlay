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

        self.overlay_left = create_overlay(x=75, y=175, w=300, h=180)
        self.overlay_middle = create_overlay(x=275, y=175, w=300, h=180)
        self.overlay_right = create_overlay(x=475, y=175, w=300, h=180)

        self.overlays = [
            self.overlay_left,
            self.overlay_middle,
            self.overlay_right,
        ]

        # One cache entry per overlay slot
        self.last_overlay_data = [None, None, None]

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

    def make_overlay_data(self, match):
        return (
            match["boss_name"],
            match["standard"],
            match["slash"],
            match["strike"],
            match["pierce"],
            match["magic"],
            match["fire"],
            match["lightning"],
            match["holy"],
        )

    def update_overlay(self, overlay, match):
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

        overlay.set_overlay(
            match["boss_name"],
            left_rows,
            right_rows
        )

    def clear_overlay(self, overlay):
        overlay.set_overlay("", [], [])

    def scan_once(self):
        boss_names = self.scanner.scan_boss_names()
        matches = self.database.find_best_matches(boss_names)

        for i, overlay in enumerate(self.overlays):
            if i < len(matches):
                match = matches[i]
                new_data = self.make_overlay_data(match)

                # Only redraw if something actually changed
                if self.last_overlay_data[i] != new_data:
                    self.print_match(match)
                    self.update_overlay(overlay, match)
                    self.last_overlay_data[i] = new_data
            else:
                # No match for this slot anymore -> clear once
                if self.last_overlay_data[i] is not None:
                    self.clear_overlay(overlay)
                    self.last_overlay_data[i] = None

        Window.after(int(SCAN_INTERVAL * 1000), self.scan_once)

    def run(self):
        Window.after(100, self.scan_once)
        Window.launch()


if __name__ == "__main__":
    app = BossApp()
    app.run()