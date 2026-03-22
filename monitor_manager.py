from screeninfo import get_monitors

# ── Overlay layout (fractions of screen size) ────────────
# Derived from 1920×1080 reference: x=75, y=175, w=300, h=180, spacing=200
OVERLAY_X_START  = 0.039    # 75 / 1920
OVERLAY_Y        = 0.162    # 175 / 1080
OVERLAY_W        = 0.156    # 300 / 1920
OVERLAY_H        = 0.167    # 180 / 1080
OVERLAY_SPACING  = 0.104    # 200 / 1920  (x distance between overlay starts)

# ── Boss‑bar vertical spacing (fraction of height) ──────
# Measured gap between stacked boss bars in Elden Ring
BAR_STEP = 0.081250


class MonitorManager:
    def __init__(self):
        self.width = 0
        self.height = 0
        self._detect_primary_monitor()

    def _detect_primary_monitor(self):
        for m in get_monitors():
            if m.is_primary:
                self.width = m.width
                self.height = m.height
                return

        raise RuntimeError("No primary monitor found.")

    def get_regions(self):
        """Returns text scan regions for each boss name position (lower → upper)."""
        return [
            {   # Region 0 — lowest boss name
                "left":   int(self.width  * 0.237891),
                "top":    int(self.height * 0.761111),
                "width":  int(self.width  * 0.168750),
                "height": int(self.height * 0.027083),
            },
            {   # Region 1 — middle boss name
                "left":   int(self.width  * 0.237109),
                "top":    int(self.height * (0.761111 - BAR_STEP)),
                "width":  int(self.width  * 0.166797),
                "height": int(self.height * 0.025694),
            },
            {   # Region 2 — top boss name
                "left":   int(self.width  * 0.237109),
                "top":    int(self.height * (0.761111 - BAR_STEP * 2)),
                "width":  int(self.width  * 0.166797),
                "height": int(self.height * 0.025694),
            },
        ]

    def get_boss_bar_regions(self):
        """Returns a small sample region on each boss's health bar.
        One per text region, in the same order."""
        base_x = 0.242969
        base_y = 0.797222
        return [
            {   # Lower boss bar
                "left":   int(self.width  * base_x),
                "top":    int(self.height * base_y),
                "width":  2,
                "height": 2,
            },
            {   # Middle boss bar
                "left":   int(self.width  * base_x),
                "top":    int(self.height * (base_y - BAR_STEP)),
                "width":  2,
                "height": 2,
            },
            {   # Top boss bar
                "left":   int(self.width  * base_x),
                "top":    int(self.height * (base_y - BAR_STEP * 2)),
                "width":  2,
                "height": 2,
            },
        ]

    def get_overlay_positions(self):
        """Returns (x, y, w, h) for each overlay, scaled to monitor size."""
        positions = []
        for i in range(3):
            x = int(self.width  * (OVERLAY_X_START + OVERLAY_SPACING * i))
            y = int(self.height * OVERLAY_Y)
            w = int(self.width  * OVERLAY_W)
            h = int(self.height * OVERLAY_H)
            positions.append((x, y, w, h))
        return positions


