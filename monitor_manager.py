from screeninfo import get_monitors


class MonitorManager:
    def __init__(self):
        self.width = 0
        self.height = 0
        self._detect_primary_monitor()
        self.create_boss_bar_region()

    def _detect_primary_monitor(self):
        for m in get_monitors():
            if m.is_primary:
                self.width = m.width
                self.height = m.height
                return

        raise RuntimeError("No primary monitor found.")

    def create_boss_bar_region(self):
        region = {
            "left": int(self.width * 0.242969),
            "top": int(self.height * 0.797222),
            "width": 2,
            "height": 2,
        }
        return region


    def get_regions(self):
        return [
            {
                "left": int(self.width * 0.237891),
                "top": int(self.height * 0.761111),
                "width": int(self.width * 0.168750),
                "height": int(self.height * 0.027083),
            },
            {
                "left": int(self.width * 0.237109),
                "top": int(self.height * 0.679861),
                "width": int(self.width * 0.166797),
                "height": int(self.height * 0.025694),
            }
        ]

