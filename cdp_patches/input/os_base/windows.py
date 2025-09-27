import asyncio
import ctypes
import re
import time
import warnings
from typing import List, Literal, Union

from pywinauto import application, timings, win32defines, win32functions, win32structures
from pywinauto.application import WindowSpecification
from pywinauto.base_wrapper import ElementNotVisible
from pywinauto.controls.hwndwrapper import HwndWrapper, InvalidWindowHandle, _calc_flags_and_coords

from cdp_patches.input.exceptions import WindowClosedException

timings.Timings.fast()
timings.TimeConfig._timings["sendmessagetimeout_timeout"] = 0
timings.TimeConfig._timings["after_click_wait"] = 0
timings.TimeConfig._timings["after_clickinput_wait"] = 0
timings.TimeConfig._timings["after_sendkeys_key_wait"] = 0
# don't block asyncio
timings.TimeConfig._timings["scroll_step_wait"] = 0.01
timings.TimeConfig._timings["window_find_timeout"] = 0.01
timings.TimeConfig._timings["exists_timeout"] = 0.01

warnings.filterwarnings("ignore", category=UserWarning, message="32-bit application should be automated using 32-bit Python (you use 64-bit Python)")


def get_top_window(app: application.Application, windows=List[Union[WindowSpecification, HwndWrapper]]) -> WindowSpecification:
    if windows is None:
        windows = app
    # win32_app.top_window(), but without timeout
    criteria = {"backend": app.backend.name}
    if windows[0].handle:
        criteria["handle"] = windows[0].handle
    else:
        criteria["name"] = windows[0].name
    return WindowSpecification(criteria, allow_magic_lookup=app.allow_magic_lookup)


class WindowsBase:
    browser_window: Union[WindowSpecification, HwndWrapper]
    hwnd: int
    pid: int
    scale_factor: float = 1.0
    toolbar_height: int = 0
    win32_app: application.Application = None

    def __init__(self, pid: int, scale_factor: float) -> None:
        self.pid = pid
        self.scale_factor = scale_factor
        self._loop = asyncio.get_event_loop()

    def include_windows_scale_factor(self):
        windows_scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        self.scale_factor *= windows_scale_factor

    def get_window(
        self,
        timeout: float = 1,
    ) -> WindowSpecification:
        if self.win32_app is None:
            # save time
            self.win32_app = application.Application(backend="win32")
            self.win32_app.connect(process=self.pid, timeout=timeout)
        try:
            windows = self.win32_app.windows()
        except InvalidWindowHandle:
            raise WindowClosedException(pid=self.pid)
        if not windows:
            raise WindowClosedException(f"No windows found for PID: {self.pid}")
        for window in windows:
            if window.element_info.class_name == "Chrome_WidgetWin_1" and window.is_visible():
                self.browser_window = window
                break
        else:
            self.browser_window = get_top_window(self.win32_app, windows)

        for child in self.browser_window.iter_children():
            if child.element_info.class_name == "Chrome_RenderWidgetHostHWND":
                self.browser_window = child

        self.hwnd = self.browser_window.handle
        # Perform Window Checks
        try:
            self.browser_window.verify_actionable()
        except ElementNotVisible:
            raise WindowClosedException(pid=self.pid)
        if not self.browser_window.is_normal():
            raise WindowClosedException(pid=self.pid)

        return self.browser_window

    def ensure_window(self) -> None:
        try:
            if not self.browser_window.is_visible():
                self.get_window()
        except InvalidWindowHandle:
            self.get_window()

    async def async_get_window(self, timeout: float = 1) -> WindowSpecification:
        if self.win32_app is None:
            # save time
            self.win32_app = application.Application(backend="win32")
            await self._loop.run_in_executor(None, lambda: self.win32_app.connect(process=self.pid, timeout=timeout))

        windows = self.win32_app.windows()
        if not windows:
            raise WindowClosedException(f"No windows found for PID: {self.pid}")
        for window in windows:
            if window.element_info.class_name == "Chrome_WidgetWin_1" and window.is_visible():
                self.browser_window = window
                break
        else:
            self.browser_window = get_top_window(self.win32_app, windows)

        for child in self.browser_window.iter_children():
            if child.element_info.class_name == "Chrome_RenderWidgetHostHWND":
                self.browser_window = child

        self.hwnd = self.browser_window.handle
        # Perform Window Checks
        try:
            self.browser_window.verify_actionable()
        except ElementNotVisible:
            raise WindowClosedException(pid=self.pid)
        if not self.browser_window.is_normal():
            raise WindowClosedException(pid=self.pid)

        return self.browser_window

    def down(self, button: Literal["left", "right", "middle"], x: int, y: int, pressed: str = "") -> None:
        if not pressed:
            pressed = button
        self.ensure_window()
        self.browser_window.press_mouse(button=button, pressed=pressed, coords=(int(x * self.scale_factor), int(y * self.scale_factor)))

    def double_click(self, button: Literal["left", "right", "middle"], x: int, y: int, pressed: str = "", press_timeout: float = 0.01, click_timeout: float = 0.15) -> None:
        if not pressed:
            pressed = button
        flags, click_point = _calc_flags_and_coords(pressed, [x, y])

        self.ensure_window()

        if button.lower() == "left":
            click = (win32defines.WM_LBUTTONDOWN, win32defines.WM_LBUTTONUP)
        elif button.lower() == "right":
            click = (win32defines.WM_RBUTTONDOWN, win32defines.WM_RBUTTONUP)
        else:
            click = (win32defines.WM_MBUTTONDOWN, win32defines.WM_MBUTTONUP)

        # figure out the flags and pack coordinates
        for i in range(2):
            for msg in click:
                win32functions.PostMessage(self.browser_window, msg, win32structures.WPARAM(flags), win32structures.LPARAM(click_point))
                time.sleep(press_timeout)
                # wait until the thread can accept another message
                win32functions.WaitGuiThreadIdle(self.browser_window.handle)
            if not i:
                time.sleep(click_timeout)

    def up(self, button: Literal["left", "right", "middle"], x: int, y: int, pressed: str = "") -> None:
        self.ensure_window()
        self.browser_window.release_mouse(button=button, pressed=pressed, coords=(int(x * self.scale_factor), int(y * self.scale_factor)))

    def move(self, x: int, y: int, pressed: str = "") -> None:
        self.ensure_window()
        self.browser_window.move_mouse(coords=(int(x * self.scale_factor), int(y * self.scale_factor)), pressed=pressed)

    def scroll(self, direction: Literal["up", "down", "left", "right"], amount: int) -> None:
        self.ensure_window()
        self.browser_window.scroll(direction=direction, amount="line", count=int(amount * self.scale_factor))

    def send_keystrokes(self, text: str) -> None:
        # Unmodifying Pywinauto's modifiers & adding down/up modifiers
        modified_text = ""
        selective_regex = re.compile(r"{[^{}]*}|.")

        for key in selective_regex.findall(text):
            if key in ["+", "^", "%", "~"]:
                key = "{" + key + "}"

            modified_text += key

        self.ensure_window()
        self.browser_window.send_keystrokes(modified_text)
