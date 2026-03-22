import tkinter as tk
import os

windows = []
BG = "#010101"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Window:
    main = None

    def __init__(self, title="", x=0, y=100, w=360, h=180):
        self.root = tk.Tk() if Window.main is None else tk.Toplevel(Window.main)
        if Window.main is None:
            Window.main = self.root

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=BG)
        self.root.wm_attributes("-transparentcolor", BG)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.alive = True
        self.images = {}
        windows.append(self)

        self.container = tk.Frame(self.root, bg=BG)
        self.container.pack(expand=True, fill="both", padx=8, pady=8)

        self.title_var = tk.StringVar(value=title)
        self.title_label = tk.Label(
            self.container,
            textvariable=self.title_var,
            fg="white",
            bg=BG,
            font=("Bahnschrift", 11, "bold"),
            anchor="w",
            justify="left",
            bd=0,
            highlightthickness=0
        )
        self.title_label.pack(fill="x", pady=(0, 3))

        self.grid_frame = tk.Frame(self.container, bg=BG)
        self.grid_frame.pack(fill="both", expand=False)

    def get_icon(self, path):
        full_path = os.path.join(BASE_DIR, path)
        if full_path not in self.images:
            try:
                img = tk.PhotoImage(file=full_path)
                self.images[full_path] = img.subsample(2, 2)
            except tk.TclError as e:
                print(f"Failed to load icon: {full_path}\n{e}")
                self.images[full_path] = None
        return self.images[full_path]

    def clear_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

    def set_overlay(self, boss_name, left_rows, right_rows):
        if not self.alive:
            return

        self.title_var.set(str(boss_name))
        self.clear_grid()

        self.grid_frame.grid_columnconfigure(0, weight=0)
        self.grid_frame.grid_columnconfigure(1, weight=0)

        max_rows = max(len(left_rows), len(right_rows))
        for row in range(max_rows):
            if row < len(left_rows):
                self._add_pair(row, 0, left_rows[row][0], left_rows[row][1])
            if row < len(right_rows):
                self._add_pair(row, 1, right_rows[row][0], right_rows[row][1])

    def _add_pair(self, row, col, icon_path, value):
        frame = tk.Frame(self.grid_frame, bg=BG)
        frame.grid(row=row, column=col, sticky="w", padx=6, pady=0)

        icon = self.get_icon(icon_path)
        if icon is not None:
            icon_label = tk.Label(
                frame,
                image=icon,
                bg=BG,
                bd=0,
                highlightthickness=0
            )
            icon_label.image = icon
            icon_label.pack(side="left", padx=(0, 6))
        else:
            fallback = tk.Label(
                frame,
                text="[x]",
                fg="red",
                bg=BG,
                font=("Arial", 9, "bold"),
                bd=0,
                highlightthickness=0
            )
            fallback.pack(side="left", padx=(0, 6))

        value_label = tk.Label(
            frame,
            text=str(value),
            fg="white",
            bg=BG,
            font=("Arial", 10, "bold"),
            bd=0,
            highlightthickness=0,
            anchor="w"
        )
        value_label.pack(side="left")

    def destroy(self):
        if not self.alive:
            return

        self.alive = False
        if self in windows:
            windows.remove(self)

        try:
            if self.root.winfo_exists():
                self.root.destroy()
        except tk.TclError:
            pass

        if not windows:
            Window.main = None

    @classmethod
    def after(cls, ms, func, *args):
        if cls.main is not None:
            try:
                cls.main.after(ms, func, *args)
            except tk.TclError:
                pass

    @classmethod
    def destroy_all(cls):
        for w in windows[:]:
            w.destroy()

    @classmethod
    def launch(cls):
        if cls.main is not None:
            try:
                cls.main.mainloop()
            except tk.TclError:
                pass


def _format_value(entities, key):
    """Format a stat value across one or more entities.
    Single entity:  '35'
    Multi entity:   '35 / 0'"""
    values = [str(e[key]) for e in entities]
    return " / ".join(values)


def build_rows(entities):
    """Build icon+value rows from a list of entity dicts.

    entities: list of dicts, each with keys like 'standard', 'slash', etc.
    For dual-entity bosses the list has 2 items → values show as 'v1 / v2'.
    """
    left_rows = [
        ("src/standard-damage.png",  _format_value(entities, "standard")),
        ("src/slash-damage.png",     _format_value(entities, "slash")),
        ("src/strike-damage.png",    _format_value(entities, "strike")),
        ("src/pierce-damage.png",    _format_value(entities, "pierce")),
    ]

    right_rows = [
        ("src/magic-affinity.png",      _format_value(entities, "magic")),
        ("src/fire-affinity.png",       _format_value(entities, "fire")),
        ("src/lightning-affinity.png",  _format_value(entities, "lightning")),
        ("src/holy-affinity.png",       _format_value(entities, "holy")),
    ]

    return left_rows, right_rows


def start_overlay(
    boss,
    entities,
    x=75,
    y=175,
    w=300,
    h=180
):
    win = Window(x=x, y=y, w=w, h=h)
    left_rows, right_rows = build_rows(entities)
    Window.after(100, win.set_overlay, boss, left_rows, right_rows)
    Window.launch()


def create_overlay(x=75, y=175, w=300, h=180):
    return Window(x=x, y=y, w=w, h=h)