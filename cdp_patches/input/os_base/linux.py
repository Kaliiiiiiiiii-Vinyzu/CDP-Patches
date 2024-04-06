import re
import subprocess
import time
from typing import Any, Literal, Tuple

from xdo import Xdo
from Xlib import X, display
from Xlib.ext.xtest import fake_input
from Xlib.XK import string_to_keysym
from Xlib.xobject.drawable import Window

xdo = Xdo()

symbol_dict = {  # Every Common Symbol on a QWERTY Keyboard, Source: https://github.com/python-xlib/python-xlib/blob/4e8bbf8fc4941e5da301a8b3db8d27e98de68666/Xlib/keysymdef/latin1.py
    "+": "plus",
    "-": "minus",
    "*": "asterisk",
    "/": "slash",
    "^": "asciicircum",
    "%": "percent",
    "=": "equal",
    "<": "less",
    ">": "greater",
    "&": "ampersand",
    "|": "bar",
    "!": "exclam",
    "~": "asciitilde",
    "`": "grave",
    "@": "at",
    "#": "numbersign",
    "$": "dollar",
    "_": "underscore",
    "[": "bracketleft",
    "]": "bracketright",
    "{": "braceleft",
    "}": "braceright",
    "(": "parenleft",
    ")": "parenright",
    ":": "colon",
    ";": "semicolon",
    ",": "comma",
    ".": "period",
    "?": "question",
    "\\": "backslash",
    '"': "quotedbl",
    "'": "quoteright",
    " ": "space",
}

layouts_shifted_chars = {
    "QWERTY": '~!@#$%^&*()_+{}|:"<>?',
    "AZERTY": '^¨£$¤%µ§*()_+{}|:"<>?',
    "QWERTZ": '°!"§$%&/()=?`´*_:;<>|',
    "DVORAK": '~!@#$%^&*()_+{}|:"<>?',
    "COLEMAK": '~!@#$%^&*()_+{}|:"<>?',
    "WORKMAN": '~!@#$%^&*()_+{}|:"<>?',
    "BEPO": '~!@#$%^&*()_+{}|:"<>?',
    "NEO": '~!@#$%^&*()_+{}|:"<>?',
    "JCUKEN": '!"№;%:?*()_+{}|:"<>?',
    "RUSSIAN": '!"№;%:?*()_+{}|:"<>?',
}


# Note for someday: `setxkbmap us`
def get_kb_layout_shifted_chars() -> str:
    search_regex = r'xkb_keycodes\s+{\s+include\s+"[A-Za-z\+]*\((.*?)\)"'
    layout_info = subprocess.check_output(["setxkbmap", "-print"]).decode("utf-8")
    matches = re.search(search_regex, layout_info)
    if matches:
        layout = matches.group(1).upper()
        if layout in layouts_shifted_chars:
            return layouts_shifted_chars[layout]
        raise EnvironmentError(f"Keyboard layout not recognized: {layout}!")
    raise EnvironmentError("Keyboard layout not found!")


class LinuxBase:
    browser_window: Window
    hwnd: int
    pid: int
    scale_factor: float = 1.0
    toolbar_height: int = 0
    render_widget_height: int = 0
    shifted_chars = get_kb_layout_shifted_chars()

    def __init__(self, pid: int, scale_factor: float) -> None:
        self.pid = pid
        self.scale_factor = scale_factor

        self.display = display.Display()
        self.tab_pid = self.get_window()

        self.browser_window = self.display.create_resource_object("window", self.tab_pid)

    def get_window(self) -> Any:
        res_windows = xdo.search_windows(pid=self.pid)

        for window in res_windows:
            window_size = xdo.get_window_size(window)
            title = xdo.get_window_name(window)

            # Filtering out helper windows (like the taskbar)
            if (title == b"google-chrome") or (window_size.width == window_size.height):
                continue

            return window

        raise ValueError("No browser window found")

    def _offset_toolbar_height(self) -> Tuple[int, int]:
        window_location = xdo.get_window_location(self.tab_pid)

        # Get Chrome Toolbar Height (Note: Fetching Chromes "Program Specified Minimum Size" - 1 for Chrome Toolbar Height + 1 for the Minimum Tab Size)
        normal_hints_atom = self.display.get_atom("WM_NORMAL_HINTS", only_if_exists=True)
        if normal_hints_atom == X.NONE:
            raise ValueError('No Atom interned with the Name "WM_NORMAL_HINTS".')

        normal_hints = self.browser_window.get_property(normal_hints_atom, 0, 0, pow(2, 32) - 1)
        chrome_toolbar_height = normal_hints.value[6] - 1

        # Get Linux (Outer) Window Toolbar Height
        frame_extends_atom = self.display.get_atom("_NET_FRAME_EXTENTS", only_if_exists=True)
        if frame_extends_atom == X.NONE:
            raise ValueError('No Atom interned with the Name "_NET_FRAME_EXTENTS".')

        net_frame_extends = self.browser_window.get_property(frame_extends_atom, 0, 0, pow(2, 32) - 1)
        window_toolbar_height = net_frame_extends.value[2]
        window_toolbar_width = net_frame_extends.value[3]

        offset_width: int = window_location.x - window_toolbar_width
        offset_height: int = window_location.y - window_toolbar_height + chrome_toolbar_height
        return offset_width, offset_height

    @staticmethod
    def _translate_button(button: Literal["left", "right", "middle", "scroll_up", "scroll_down"]) -> int:
        if button == "left":
            return 1
        elif button == "middle":
            return 2
        elif button == "right":
            return 3
        elif button == "scroll_up":
            return 4
        elif button == "scroll_down":
            return 5

    def down(self, button: Literal["left", "right", "middle"], x: int, y: int) -> None:
        self.move(x=x, y=y)
        fake_input(self.display, X.ButtonPress, self._translate_button(button))
        self.display.sync()

    def up(self, button: Literal["left", "right", "middle"], x: int, y: int) -> None:
        self.move(x=x, y=y)
        fake_input(self.display, X.ButtonRelease, self._translate_button(button))
        self.display.sync()

    def move(self, x: int, y: int) -> None:
        offset_width, offset_height = self._offset_toolbar_height()
        x = int(x * self.scale_factor) + offset_width
        y = int(y * self.scale_factor) + offset_height

        fake_input(self.display, X.MotionNotify, x=x, y=y)
        self.display.sync()

    def scroll(self, direction: Literal["up", "down", "left", "right"], amount: int) -> None:
        if direction in ("left", "right"):
            raise NotImplementedError("Scrolling horizontally is not supported on Linux.")

        scroll_direction: Literal["scroll_up", "scroll_down"] = "scroll_up" if direction == "up" else "scroll_down"

        for _ in range(amount):
            fake_input(self.display, X.ButtonPress, self._translate_button(scroll_direction))
            self.display.sync()
            fake_input(self.display, X.ButtonRelease, self._translate_button(scroll_direction))
            self.display.sync()

    def send_keystrokes(self, text: str) -> None:
        selective_regex = re.compile(r"{[^{}]*}|.")  # Only for redundancy of windows implementations
        shift_keycode = self.display.keysym_to_keycode(0xFFE1)  # Shift Key (0xFFE1)

        for key in selective_regex.findall(text):
            shifted_key = key.isupper() or key in self.shifted_chars
            if key in symbol_dict:
                key = symbol_dict[key]

            keysym = string_to_keysym(key)
            keycode = self.display.keysym_to_keycode(keysym)
            self.browser_window.set_input_focus(X.RevertToNone, X.CurrentTime)

            if shifted_key:
                fake_input(self.display, X.KeyPress, shift_keycode)
                # time.sleep(0.1)

            fake_input(self.display, X.KeyPress, keycode)
            self.display.sync()
            time.sleep(0.01)  # Note: Might want to increase this in the future, to make it more human-like, but pywinauto uses the same timeouts so for now its fine.

            fake_input(self.display, X.KeyRelease, keycode)

            if shifted_key:
                # time.sleep(0.1)
                fake_input(self.display, X.KeyRelease, shift_keycode)
            self.display.sync()
