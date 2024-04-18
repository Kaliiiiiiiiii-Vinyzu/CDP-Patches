import asyncio
import os
import re
import subprocess
import time
from typing import Any, List, Literal, Tuple

from Xlib import X, display
from Xlib.error import BadWindow
from Xlib.ext.xtest import fake_input
from Xlib.XK import string_to_keysym
from Xlib.xobject.drawable import Window

from cdp_patches.input.exceptions import WindowClosedException

# Every Common Symbol on a QWERTY Keyboard, Source: https://github.com/python-xlib/python-xlib/blob/4e8bbf8fc4941e5da301a8b3db8d27e98de68666/Xlib/keysymdef/latin1.py
# Dict Source: https://github.com/svenlr/swift-map/blob/main/mainloop.py#L459
symbol_dict = {
    "@": "at",
    "`": "grave",
    "\t": "Tab",
    "|": "bar",
    "\n": "Return",
    "\r": "Return",
    "~": "asciitilde",
    "{": "braceleft",
    "[": "bracketleft",
    "]": "bracketright",
    "\\": "backslash",
    "_": "underscore",
    "^": "asciicircum",
    "!": "exclam",
    " ": "space",
    "#": "numbersign",
    '"': "quotedbl",
    "%": "percent",
    "$": "dollar",
    "'": "apostrophe",
    "&": "ampersand",
    ")": "parenright",
    "(": "parenleft",
    "+": "plus",
    "*": "asterisk",
    "-": "minus",
    ",": "comma",
    "/": "slash",
    ".": "period",
    "\\e": "Escape",
    "}": "braceright",
    ";": "semicolon",
    ":": "colon",
    "=": "equal",
    "<": "less",
    "?": "question",
    ">": "greater",
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
        self._loop = asyncio.get_event_loop()

        display_env = os.getenv("DISPLAY")
        self.display = display.Display(display_env)
        self.tab_pid = self.get_window()

        self.browser_window = self.display.create_resource_object("window", self.tab_pid)

    def get_window(self) -> Any:
        name_atom = self.display.get_atom("WM_NAME", only_if_exists=True)
        pid_atom = self.display.get_atom("_NET_WM_PID", only_if_exists=True)
        res_windows: List[Window] = []

        # Getting all WindowIds by PID by recursively searching through all windows under the root window query tree
        def search_windows_by_pid(query_tree, pid: int):
            for window in query_tree.children:
                window_pid = window.get_property(pid_atom, 0, 0, pow(2, 32) - 1)
                if window_pid and window_pid.value[0] == pid:
                    res_windows.append(window)
                if window.query_tree().children:
                    search_windows_by_pid(window.query_tree(), pid)

        search_windows_by_pid(self.display.screen().root.query_tree(), self.pid)
        if not res_windows:
            raise WindowClosedException(f"No windows found for PID: {self.pid}")

        for window in res_windows:
            # Getting necessary window properties
            title = window.get_property(name_atom, 0, 0, pow(2, 32) - 1).value
            min_height = window.get_wm_normal_hints().min_height
            # parent_offset_coords = window.translate_coords(window.query_tree().parent, 0, 0)
            # window_x, window_y = parent_offset_coords.x, parent_offset_coords.y

            # Filter out non-browser windows, for example the Taskbar or Info Bars
            if (b"google-chrome" in title) or (title == b"chrome") or (min_height == 0):  # or (window_x == window_y) or not all((window_x, window_y))
                continue

            self.browser_window = window
            return self.browser_window

        raise WindowClosedException(f"No windows found for PID: {self.pid}")

    def ensure_window(self) -> None:
        try:
            # No Easy Visibility Check, well just check a random window attribute...
            if not self.browser_window.get_wm_normal_hints().min_height:
                self.get_window()
        except BadWindow:
            self.get_window()

    async def async_get_window(self) -> Any:
        name_atom = self.display.get_atom("WM_NAME", only_if_exists=True)
        pid_atom = self.display.get_atom("_NET_WM_PID", only_if_exists=True)
        res_windows: List[Window] = []

        # Getting all WindowIds by PID by recursively searching through all windows under the root window query tree
        def search_windows_by_pid(query_tree, pid: int):
            for window in query_tree.children:
                window_pid = window.get_property(pid_atom, 0, 0, pow(2, 32) - 1)
                if window_pid and window_pid.value[0] == pid:
                    res_windows.append(window)
                if window.query_tree().children:
                    search_windows_by_pid(window.query_tree(), pid)

        await self._loop.run_in_executor(None, lambda: search_windows_by_pid(self.display.screen().root.query_tree(), self.pid))
        if not res_windows:
            raise WindowClosedException(f"No windows found for PID: {self.pid}")

        for window in res_windows:
            # Getting necessary window properties
            title = window.get_property(name_atom, 0, 0, pow(2, 32) - 1).value
            min_height = window.get_wm_normal_hints().min_height
            # parent_offset_coords = window.translate_coords(window.query_tree().parent, 0, 0)
            # window_x, window_y = parent_offset_coords.x, parent_offset_coords.y

            # Filter out non-browser windows, for example the Taskbar or Info Bars
            if (b"google-chrome" in title) or (title == b"chrome") or (min_height == 0):  # or (window_x == window_y) or not all((window_x, window_y))
                continue

            self.browser_window = window
            return self.browser_window

        raise WindowClosedException(f"No windows found for PID: {self.pid}")

    def _offset_toolbar_height(self) -> Tuple[int, int]:
        # Get Window Location
        root_offset_coords = self.browser_window.translate_coords(self.browser_window.query_tree().root, 0, 0)
        parent_offset_coords = self.browser_window.translate_coords(self.browser_window.query_tree().parent, 0, 0)
        window_x = abs(root_offset_coords.x) + abs(parent_offset_coords.x)
        window_y = abs(root_offset_coords.y) + abs(parent_offset_coords.y)

        # Get Chrome Toolbar Height (Note: Fetching Chromes "Program Specified Minimum Size" - 1 for Chrome Toolbar Height + 1 for the Minimum Tab Size)
        chrome_toolbar_height = self.browser_window.get_wm_normal_hints().min_height - 1

        # Get Linux (Outer) Window Toolbar Height
        frame_extends_atom = self.display.get_atom("_NET_FRAME_EXTENTS", only_if_exists=True)
        if frame_extends_atom == X.NONE:
            raise ValueError('No Atom interned with the Name "_NET_FRAME_EXTENTS".')

        net_frame_extends = self.browser_window.get_property(frame_extends_atom, 0, 0, pow(2, 32) - 1)
        if net_frame_extends:
            window_toolbar_height = net_frame_extends.value[2]
            window_toolbar_width = net_frame_extends.value[3]
        else:
            window_toolbar_height = 0
            window_toolbar_width = 0

        offset_width: int = window_x - window_toolbar_width
        offset_height: int = window_y - window_toolbar_height + chrome_toolbar_height
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
        self.ensure_window()
        self.move(x=x, y=y)
        fake_input(self.display, X.ButtonPress, self._translate_button(button))
        self.display.sync()

    def up(self, button: Literal["left", "right", "middle"], x: int, y: int) -> None:
        self.ensure_window()
        self.move(x=x, y=y)
        fake_input(self.display, X.ButtonRelease, self._translate_button(button))
        self.display.sync()

    def move(self, x: int, y: int) -> None:
        self.ensure_window()
        offset_width, offset_height = self._offset_toolbar_height()
        x = int(x * self.scale_factor) + offset_width
        y = int(y * self.scale_factor) + offset_height

        fake_input(self.display, X.MotionNotify, x=x, y=y)
        self.display.sync()

    def scroll(self, direction: Literal["up", "down", "left", "right"], amount: int) -> None:
        self.ensure_window()
        if direction in ("left", "right"):
            raise NotImplementedError("Scrolling horizontally is not supported on Linux.")

        scroll_direction: Literal["scroll_up", "scroll_down"] = "scroll_up" if direction == "up" else "scroll_down"

        for _ in range(amount):
            fake_input(self.display, X.ButtonPress, self._translate_button(scroll_direction))
            self.display.sync()
            fake_input(self.display, X.ButtonRelease, self._translate_button(scroll_direction))
            self.display.sync()

    def send_keystrokes(self, text: str) -> None:
        self.ensure_window()
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
