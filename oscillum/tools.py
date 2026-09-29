# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# project:  auditus - Oscillum
# authors:  Giuseppe Costanzi (1966bc)
# licence:  MIT, see LICENSE
# -----------------------------------------------------------------------------
"""Widget helpers: theme, geometry, factories, cursor.

A trimmed copy of the Tools class of Tkinterlite: only what Oscillum uses.
One job: helping to build widgets.
"""

import tkinter as tk
from tkinter import font
from tkinter import ttk


class Tools:
    """Appearance and behaviour shared by every window."""

    # --- palette ------------------------------------------------------------
    # Meaning first, hue second: the names say what a colour is for.
    BACKGROUND = (240, 240, 237)
    FOREGROUND = (0, 0, 0)
    WHITE = (255, 255, 255)
    EMPHASIS = (255, 0, 0)              # the one thing that must be seen first
    BORDER = (169, 169, 165)            # the outline of anything with an edge
    TROUGH = (222, 222, 218)            # scrollbar channel
    HOVER = (228, 231, 235)             # under the pointer
    PRESSED = (205, 209, 214)           # while the mouse is down
    FOCUS = (58, 110, 165)              # where the keyboard is
    SELECTED = (51, 103, 158)           # the chosen row, the selected text
    UNAVAILABLE = (150, 150, 150)       # a control that is disabled

    # The charts: a grid that stays behind the data, and one colour per
    # channel. The left channel takes the colour of the focus, the right one
    # a warm colour, so the two never read as one when they overlap.
    GRID = (222, 222, 218)
    LEFT = (58, 110, 165)
    RIGHT = (214, 120, 40)
    LABEL = (110, 110, 105)             # the words on an axis

    #: Every button in a button column is at least this wide. Negative, because
    #: ttk reads a negative width as a minimum.
    BUTTON_WIDTH = -8

    BUSY_CURSOR = "watch"

    def __str__(self):
        return "class: {0}".format(self.__class__.__name__)

    # --- theme --------------------------------------------------------------

    def get_rgb(self, red, green, blue):
        """An (r, g, b) triple as the hex string tkinter expects."""
        return "#{0:02x}{1:02x}{2:02x}".format(red, green, blue)

    def set_style(self, theme):
        """Configure every style the application uses.

        Meant for 'clam': it exists on Windows and on Linux and looks the same
        on both, and it is the only built-in theme whose colours are settable.
        """
        self.style = ttk.Style()

        if theme in self.style.theme_names():
            self.style.theme_use(theme)
        else:
            raise ValueError("unknown ttk theme: {0}".format(theme))

        background = self.get_rgb(*self.BACKGROUND)
        foreground = self.get_rgb(*self.FOREGROUND)
        white = self.get_rgb(*self.WHITE)
        border = self.get_rgb(*self.BORDER)
        trough = self.get_rgb(*self.TROUGH)
        hover = self.get_rgb(*self.HOVER)
        pressed = self.get_rgb(*self.PRESSED)
        focus = self.get_rgb(*self.FOCUS)
        selected = self.get_rgb(*self.SELECTED)
        unavailable = self.get_rgb(*self.UNAVAILABLE)
        base = font.nametofont("TkDefaultFont")

        self.style.configure(".",
                             background=background,
                             foreground=foreground,
                             fieldbackground=white,
                             bordercolor=border,
                             lightcolor=background,
                             darkcolor=background,
                             troughcolor=trough,
                             selectbackground=selected,
                             selectforeground=white,
                             font="TkDefaultFont")
        self.style.map(".", foreground=[("disabled", unavailable)])

        self.set_classic(self.style.master)

        self.style.configure("App.TFrame", background=background)
        self.style.configure("App.TLabel", padding=2, anchor=tk.W)

        # A button answers the pointer: without a map nothing on the screen
        # ever acknowledges the mouse.
        self.style.configure("App.TButton",
                             padding=(6, 5), anchor=tk.CENTER,
                             borderwidth=1, relief=tk.SOLID)
        self.style.map("App.TButton",
                       background=[("pressed", pressed),
                                   ("active", hover),
                                   ("disabled", background)],
                       bordercolor=[("pressed", focus),
                                    ("active", focus),
                                    ("focus", focus),
                                    ("disabled", border)],
                       lightcolor=[("pressed", pressed), ("active", hover)],
                       darkcolor=[("pressed", pressed), ("active", hover)])
        self.style.layout("App.TButton", self.get_layout_without("App.TButton", "focus"))

        self.style.configure("App.TLabelframe",
                             relief=tk.SOLID, borderwidth=1, padding=4,
                             bordercolor=border,
                             lightcolor=background, darkcolor=background)
        self.style.configure("App.TLabelframe.Label", background=background, padding=(2, 0))

        self.style.configure("TCombobox",
                             padding=(6, 4),
                             arrowsize=13, arrowcolor=foreground,
                             lightcolor=white, darkcolor=white)
        self.style.map("TCombobox",
                       bordercolor=[("focus", focus)],
                       lightcolor=[("focus", focus)],
                       darkcolor=[("focus", focus)],
                       foreground=[("readonly", "focus", foreground),
                                   ("disabled", unavailable)],
                       fieldbackground=[("readonly", white),
                                        ("disabled", background)],
                       arrowcolor=[("disabled", unavailable)])

        self.style.configure("App.TCheckbutton", padding=4,
                             indicatorbackground=white,
                             indicatorforeground=foreground,
                             focuscolor=background)
        self.style.map("App.TCheckbutton",
                       background=[("active", background)],
                       indicatorbackground=[("pressed", hover), ("disabled", background)],
                       bordercolor=[("focus", focus)])

        self.style.configure("TScrollbar",
                             troughcolor=trough, background=border,
                             bordercolor=trough, arrowcolor=foreground,
                             borderwidth=0, relief=tk.FLAT,
                             arrowsize=13, width=13)
        self.style.map("TScrollbar", background=[("pressed", focus), ("active", pressed)])

        self.style.configure("TSeparator", background=border)

        # The status bar carries colours only; its relief is written where
        # the window builds it.
        self.style.configure("StatusBar.TFrame",
                             bordercolor=background,
                             darkcolor=border, lightcolor=background)
        self.style.configure("StatusBar.TLabel",
                             padding=(6, 4), border=0, relief=tk.FLAT,
                             font="TkDefaultFont")

        self.style.configure("Title.TLabel",
                             font=(base.cget("family"), base.cget("size") + 6, "bold"))
        self.style.configure("Link.TLabel",
                             foreground=focus,
                             font=(base.cget("family"), base.cget("size"), "underline"))

    def set_classic(self, root):
        """Colour the widgets ttk cannot reach: menus and texts.

        They are set through the option database, Tk's own 'unless told
        otherwise', so this must run before any window exists.
        """
        if root is not None:
            background = self.get_rgb(*self.BACKGROUND)
            foreground = self.get_rgb(*self.FOREGROUND)
            white = self.get_rgb(*self.WHITE)
            selected = self.get_rgb(*self.SELECTED)
            unavailable = self.get_rgb(*self.UNAVAILABLE)

            for pattern, value in (
                    ("*Menu.background", background),
                    ("*Menu.foreground", foreground),
                    ("*Menu.activeBackground", selected),
                    ("*Menu.activeForeground", white),
                    ("*Menu.disabledForeground", unavailable),
                    ("*Menu.activeBorderWidth", "0"),
                    ("*Menu.relief", "flat"),
                    ("*Menu.borderWidth", "1"),
                    ("*Text.background", white),
                    ("*Text.foreground", foreground),
                    ("*Text.selectBackground", selected),
                    ("*Text.selectForeground", white),
                    ("*Text.highlightThickness", "0"),
                    ("*Text.borderWidth", "1"),
                    ("*Text.relief", "solid"),
                    ("*TCombobox*Listbox.background", white),
                    ("*TCombobox*Listbox.foreground", foreground),
                    ("*TCombobox*Listbox.selectBackground", selected),
                    ("*TCombobox*Listbox.selectForeground", white),
                    ("*TCombobox*Listbox.borderWidth", "0")):
                root.option_add(pattern, value)

    def get_layout_without(self, style_name, element):
        """This style's layout with one element taken out of it.

        Removing a node means putting its children where it was: the focus
        ring wraps the padding that holds the label, so dropping the branch
        would drop the text as well.
        """
        def prune(layout):
            kept = []
            for name, options in layout:
                options = dict(options)
                children = options.get("children")
                if children:
                    options["children"] = prune(children)
                if name.split(".")[-1] == element:
                    kept.extend(options.get("children", []))
                else:
                    kept.append((name, options))
            return kept

        return prune(self.style.layout(style_name))

    # --- geometry -----------------------------------------------------------

    def hide_me(self, container):
        """Take a window off the screen while it is being built."""
        container.withdraw()

    def center_me(self, container, over=None):
        """Centre a window over the one that opened it, and show it."""
        container.update_idletasks()
        width = container.winfo_reqwidth()
        height = container.winfo_reqheight()

        parent = over
        if parent is None:
            parent = container.master
        if (parent is not None and parent.winfo_exists()
                and parent.winfo_width() > 1):
            x = parent.winfo_rootx() + (parent.winfo_width() - width) / 2
            y = parent.winfo_rooty() + (parent.winfo_height() - height) / 2
        else:
            x = (container.winfo_screenwidth() - width) / 2
            y = (container.winfo_screenheight() - height) / 2

        x = max(0, min(int(x), container.winfo_screenwidth() - width))
        y = max(0, min(int(y), container.winfo_screenheight() - height))
        container.geometry("+{0:d}+{1:d}".format(x, y))
        container.deiconify()

    def set_geometry(self, window, width, height):
        """Give a window this size, centred on the screen and kept whole on it."""
        x = max(0, (window.winfo_screenwidth() - width) // 2)
        y = max(0, (window.winfo_screenheight() - height) // 2)
        window.geometry("{0:d}x{1:d}+{2:d}+{3:d}".format(width, height, x, y))

    # --- widget factories ---------------------------------------------------

    def get_combo(self, container):
        """Build a readonly Combobox: a value is chosen from the list, never typed."""
        return ttk.Combobox(container, state="readonly")

    def get_text(self, container):
        """Build a Text with its scrollbar, packed into container, for reading."""
        text = tk.Text(container, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)

        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        return text

    def set_text(self, text, content):
        """Put content in a Text built by get_text, and leave it read-only."""
        text.configure(state=tk.NORMAL)
        text.delete("1.0", tk.END)
        text.insert("1.0", content)
        text.configure(state=tk.DISABLED)

    def get_button_column(self, container, buttons, window=None):
        """A column of buttons, all the same width, each with an Alt accelerator.

        buttons is a sequence of (label, command) in the order they appear.
        """
        column = ttk.Frame(container, style="App.TFrame")
        target = window
        if target is None:
            target = container.winfo_toplevel()
        taken = set()

        for label, command in buttons:
            underline = self.get_underline(label, taken)
            ttk.Button(column, style="App.TButton", text=label,
                       width=self.BUTTON_WIDTH,
                       underline=underline, command=command).pack(fill=tk.X, padx=5, pady=5)
            if underline >= 0:
                letter = label[underline].lower()
                taken.add(letter)
                target.bind("<Alt-{0}>".format(letter), lambda evt, run=command: run())

        return column

    def get_underline(self, label, taken):
        """Which letter of this label to underline, or -1 for none."""
        found = -1
        for index, character in enumerate(label):
            if found < 0 and character.isalpha() and character.lower() not in taken:
                found = index
        return found

    # --- cursor -------------------------------------------------------------

    def get_widgets(self, container):
        """Every descendant of a container, depth first."""
        found = []
        for child in container.winfo_children():
            found.append(child)
            found.extend(self.get_widgets(child))
        return found

    def busy(self, caller):
        """Anything slower than an eyeblink is wrapped in busy/not_busy."""
        for widget in self.get_busy_widgets(caller):
            widget.config(cursor=self.BUSY_CURSOR)
        caller.update()

    def not_busy(self, caller):

        for widget in self.get_busy_widgets(caller):
            widget.config(cursor="")
        caller.update()

    def get_busy_widgets(self, caller):
        """The caller, the root, and everything inside the caller."""
        widgets = [caller, caller.nametowidget(".")]
        widgets.extend(self.get_widgets(caller))
        return widgets
