import sys

from config import DB_NAME, TESSERACT_CMD, OCR_CONFIG, SCAN_INTERVAL
from logger import VERBOSE, log
from monitor_manager import MonitorManager
from boss_scanner import BossScanner
from boss_database import BossDatabase
from overlay import create_overlay, build_rows, Window

# Number of consecutive scans a boss must appear before showing overlay
CONFIRM_THRESHOLD = 2
# Number of consecutive scans with a region's bar INACTIVE before clearing it
CLEAR_THRESHOLD = 3

REGION_LABELS = ["Lower", "Mid  ", "Upper"]



class RegionState:
    """Tracks state for one scan region (one boss slot)."""

    def __init__(self):
        self.boss_id = None          # Currently displayed boss id (or None)
        self.boss_name = None        # Displayed boss name (for logging)
        self.inactive_count = 0      # Consecutive scans with bar inactive
        self.pending_id = None       # Boss id awaiting confirmation
        self.pending_name = None     # Boss name awaiting confirmation (for logging)
        self.pending_count = 0       # How many scans the pending boss was seen
        self.overlay_data = None     # Cached overlay tuple to avoid redraws


class BossApp:
    def __init__(self):
        monitor = MonitorManager()
        regions = monitor.get_regions()
        overlay_positions = monitor.get_overlay_positions()

        print("============================================")
        print("  ERNR Boss Overlay — Running")
        print(f"  Monitor : {monitor.width}x{monitor.height}")
        print(f"  Scan    : every {SCAN_INTERVAL}s")
        print(f"  Regions : {len(regions)}")
        print(f"  Logging : {'ON (--log)' if VERBOSE else 'OFF (use --log to enable)'}")
        print("============================================")

        log(f"\nOverlay positions:")
        for i, (x, y, w, h) in enumerate(overlay_positions):
            log(f"  Overlay {i}: x={x} y={y} w={w} h={h}")

        self.scanner = BossScanner(
            regions=regions,
            tesseract_cmd=TESSERACT_CMD,
            config=OCR_CONFIG,
        )
        self.database = BossDatabase(DB_NAME)

        self.overlays = [
            create_overlay(x=x, y=y, w=w, h=h)
            for x, y, w, h in overlay_positions
        ]

        self.states = [RegionState() for _ in regions]
        self.scan_num = 0

    # ── helpers ──────────────────────────────────────────────

    @staticmethod
    def _overlay_tuple(match):
        """Hashable snapshot of match data for change detection."""
        entity_tuples = tuple(
            tuple(sorted(e.items())) for e in match["entities"]
        )
        return (match["boss_name"], entity_tuples)

    def _show_boss(self, idx, match):
        left, right = build_rows(match["entities"])
        self.overlays[idx].set_overlay(match["boss_name"], left, right)
        self.states[idx].overlay_data = self._overlay_tuple(match)

    def _clear_slot(self, idx):
        self.overlays[idx].set_overlay("", [], [])
        st = self.states[idx]
        old_name = st.boss_name or "?"
        st.boss_id = None
        st.boss_name = None
        st.overlay_data = None
        st.pending_id = None
        st.pending_name = None
        st.pending_count = 0
        return old_name

    # ── main scan loop ──────────────────────────────────────

    def scan_once(self):
        self.scan_num += 1
        scan_results = self.scanner.scan()

        log(f"\n{'='*50}")
        log(f"  Scan #{self.scan_num}")
        log(f"{'='*50}")

        for idx, result in enumerate(scan_results):
            label = REGION_LABELS[idx]
            st = self.states[idx]
            bar = result["bar_active"]
            ocr_name = result["name"]

            # ── Log region status ──
            bar_str = "ACTIVE" if bar else "inactive"
            ocr_str = f"'{ocr_name}'" if ocr_name else "(none)"
            log(f"  {label:5s}  bar={bar_str:8s}  ocr={ocr_str}")

            # ── Bar is INACTIVE → count towards clearing ──
            if not bar:
                st.inactive_count += 1
                st.pending_id = None
                st.pending_count = 0

                if st.boss_id is not None and st.inactive_count >= CLEAR_THRESHOLD:
                    old = self._clear_slot(idx)
                    log(f"         ✖ Cleared '{old}' (bar inactive for {CLEAR_THRESHOLD} scans)")
                elif st.boss_id is not None:
                    log(f"         … bar gone ({st.inactive_count}/{CLEAR_THRESHOLD}), keeping overlay")
                continue

            # ── Bar is ACTIVE ──
            st.inactive_count = 0

            # Try to match OCR text to a boss
            match = None
            if ocr_name:
                match = self.database.find_best_match(ocr_name)

            # Case 1: already showing a boss in this slot
            if st.boss_id is not None:
                if match and match["id"] == st.boss_id:
                    new_data = self._overlay_tuple(match)
                    if st.overlay_data != new_data:
                        self._show_boss(idx, match)
                        log(f"         ↻ Updated '{match['boss_name']}'")
                    else:
                        log(f"         ✔ '{st.boss_name}' (no change)")
                else:
                    # OCR failed or matched something else — keep current overlay
                    log(f"         ✔ Keeping '{st.boss_name}' (bar still active)")
                continue

            # Case 2: no boss shown yet — need confirmation
            if match is None:
                # Don't reset pending — the bar is active, OCR just had a
                # bad frame.  The pending boss is likely still there.
                if st.pending_id is not None:
                    log(f"         – No match (keeping pending '{st.pending_name}')")
                else:
                    log(f"         – No match")
                continue

            if match["id"] == st.pending_id:
                st.pending_count += 1
            else:
                st.pending_id = match["id"]
                st.pending_name = match["boss_name"]
                st.pending_count = 1

            if st.pending_count >= CONFIRM_THRESHOLD:
                st.boss_id = match["id"]
                st.boss_name = match["boss_name"]
                st.pending_id = None
                st.pending_count = 0
                self._show_boss(idx, match)
                log(f"         ★ Confirmed '{match['boss_name']}'")
            else:
                log(f"         ⏳ Pending '{match['boss_name']}' "
                      f"({st.pending_count}/{CONFIRM_THRESHOLD})")

        # ── Summary ──
        active = [st.boss_name for st in self.states if st.boss_id is not None]
        if active:
            log(f"  ── Showing: {', '.join(active)}")
        else:
            log(f"  ── No bosses displayed")

        Window.after(int(SCAN_INTERVAL * 1000), self.scan_once)

    def run(self):
        Window.after(100, self.scan_once)
        Window.launch()


if __name__ == "__main__":
    app = BossApp()
    app.run()

