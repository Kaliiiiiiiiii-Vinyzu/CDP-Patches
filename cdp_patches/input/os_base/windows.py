import asyncio
import ctypes
import re
import warnings
from typing import Literal, Union

from pywinauto import application, timings
from pywinauto.application import WindowSpecification
from pywinauto.controls.hwndwrapper import HwndWrapper

timings.Timings.fast()
timings.TimeConfig._timings["sendmessagetimeout_timeout"] = 0
timings.TimeConfig._timings["after_click_wait"] = 0

warnings.filterwarnings("ignore", category=UserWarning, message="32-bit application should be automated using 32-bit Python (you use 64-bit Python)")


class WindowsBase:
    browser_window: Union[WindowSpecification, HwndWrapper]
    hwnd: int
    pid: int
    scale_factor: float = 1.0
    toolbar_height: int = 0

    def __init__(self, pid: int, scale_factor: float) -> None:
        self.pid = pid
        self.scale_factor = scale_factor
        self._loop = asyncio.get_event_loop()

    def include_windows_scale_factor(self):
        windows_scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        self.scale_factor *= windows_scale_factor

    def get_window(self) -> WindowSpecification:
        win32_app = application.Application(backend="win32")
        win32_app.connect(process=self.pid, timeout=1)

        self.browser_window: WindowSpecification = win32_app.top_window()
        self.hwnd = self.browser_window.handle
        # Perform Window Checks
        self.browser_window.verify_actionable()
        assert self.browser_window.is_normal()

        for child in self.browser_window.iter_children():
            if child.element_info.class_name == "Chrome_RenderWidgetHostHWND":
                self.browser_window = child
        return self.browser_window

    async def async_get_window(self) -> WindowSpecification:
        win32_app = application.Application(backend="win32")
        await self._loop.run_in_executor(None, lambda: win32_app.connect(process=self.pid, timeout=1))

        self.browser_window: WindowSpecification = win32_app.top_window()
        self.hwnd = self.browser_window.handle
        # Perform Window Checks
        await self._loop.run_in_executor(None, lambda: self.browser_window.verify_actionable())
        assert self.browser_window.is_normal()

        for child in self.browser_window.iter_children():
            if child.element_info.class_name == "Chrome_RenderWidgetHostHWND":
                self.browser_window = child
        return self.browser_window

    def down(self, button: Literal["left", "right", "middle"], x: int, y: int) -> None:
        self.browser_window.press_mouse(button=button, coords=(int(x * self.scale_factor), int(y * self.scale_factor)))

    def up(self, button: Literal["left", "right", "middle"], x: int, y: int) -> None:
        self.browser_window.release_mouse(button=button, coords=(int(x * self.scale_factor), int(y * self.scale_factor)))

    def move(self, x: int, y: int) -> None:
        self.browser_window.move_mouse(coords=(int(x * self.scale_factor), int(y * self.scale_factor)), pressed="left")

    def scroll(self, direction: Literal["up", "down", "left", "right"], amount: int) -> None:
        self.browser_window.scroll(direction=direction, amount="line", count=int(amount * self.scale_factor))

    def send_keystrokes(self, text: str) -> None:
        # Unmodifying Pywinauto's modifiers & adding down/up modifiers
        modified_text = ""
        selective_regex = re.compile(r"{[^{}]*}|.")

        for key in selective_regex.findall(text):
            if key in ["+", "^", "%", "~"]:
                key = "{" + key + "}"

            modified_text += key

        self.browser_window.send_keystrokes(modified_text)
