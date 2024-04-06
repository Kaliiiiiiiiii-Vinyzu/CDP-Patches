import random
import re
import time
import warnings
from typing import Literal, Optional, TypeAlias, Union

from cdp_patches import is_windows

if is_windows:
    from pywinauto.base_wrapper import ElementNotEnabled, ElementNotVisible

    from cdp_patches.input.os_base.windows import WindowsBase  # type: ignore[assignment]

    LinuxBase: TypeAlias = WindowsBase  # type: ignore[no-redef]
    InputBase = WindowsBase  # type: ignore
    WindowErrors = (AssertionError, ValueError, ElementNotVisible, ElementNotEnabled)  # type: ignore[assignment]
else:
    from xdo.xdo import XdoException

    from cdp_patches.input.os_base.linux import LinuxBase  # type: ignore[assignment]

    WindowsBase: TypeAlias = LinuxBase  # type: ignore[no-redef]
    InputBase = LinuxBase  # type: ignore
    WindowErrors = (AssertionError, ValueError, XdoException)  # type: ignore[assignment]

from .browsers import get_sync_browser_pid, get_sync_scale_factor, sync_browsers
from .mouse_trajectory import HumanizeMouseTrajectory


class SyncInput:
    emulate_behaviour: Optional[bool] = True
    pid: Optional[int]
    # _base: Union[WindowsBase, LinuxBase]
    _base: InputBase
    window_timeout: int = 30
    _scale_factor: float = 1.0
    sleep_timeout: float = 0.01
    typing_speed: int = 50
    last_x: int = 0
    last_y: int = 0
    selective_modifiers_regex = re.compile(r"{[^{}]*}|.")

    def __init__(self, pid: Optional[int] = None, browser: Optional[sync_browsers] = None, scale_factor: Optional[float] = 1.0, emulate_behaviour: Optional[bool] = True) -> None:
        self._scale_factor = scale_factor or self._scale_factor
        self.emulate_behaviour = emulate_behaviour or self.emulate_behaviour

        if browser:
            self.pid = get_sync_browser_pid(browser)
            self._scale_factor = float(get_sync_scale_factor(browser))
        elif pid:
            self.pid = pid
        else:
            raise ValueError("You must provide a pid or a browser")

        self._base = InputBase(self.pid, self._scale_factor)  # type: ignore
        self._wait_for_window()

    @property
    def base(self) -> Union[WindowsBase, LinuxBase]:
        return self._base

    @property
    def scale_factor(self) -> float:
        return self._scale_factor

    @scale_factor.setter
    def scale_factor(self, scale_value: float) -> None:
        self._scale_factor = scale_value
        if self._base:
            self._base.scale_factor = scale_value

    def _wait_for_window(self) -> None:
        max_wait = time.time() + self.window_timeout
        while time.time() < max_wait:
            try:
                if self._base.get_window():
                    return
            except WindowErrors:
                pass
            self._sleep_timeout(0.1)

        raise TimeoutError(f"Chrome Window (PID: {self.pid}) not found in {self.window_timeout} seconds.")

    def _sleep_timeout(self, timeout: Optional[float] = None) -> None:
        timeout = timeout or self.sleep_timeout
        # if not random.randint(0, 10):
        # timeout_random = timeout / 10
        # timeout = random.uniform(timeout - timeout_random, timeout + timeout_random)

        time.sleep(timeout)
        # Perfect Precise Sleep
        # start = time.perf_counter()
        # while time.perf_counter() - start < timeout:
        #     pass

    def click(self, button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float], emulate_behaviour: Optional[bool] = True, timeout: Optional[float] = 0.07) -> None:
        x, y = int(x), int(y)

        self.down(button=button, x=x, y=y, emulate_behaviour=emulate_behaviour, timeout=timeout)
        if self.emulate_behaviour and emulate_behaviour:
            self._sleep_timeout(timeout=timeout)
        self.up(button=button, x=x, y=y)
        self.last_x, self.last_y = x, y

    def double_click(self, button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float], emulate_behaviour: Optional[bool] = True, timeout: Optional[float] = None) -> None:
        x, y = int(x), int(y)

        self.click(button=button, x=x, y=y, timeout=timeout, emulate_behaviour=emulate_behaviour)
        if emulate_behaviour and self.emulate_behaviour:
            # self._sleep_timeout(random.uniform(0.14, 0.21))
            self._sleep_timeout(timeout=timeout)
        self.click(button=button, x=x, y=y, emulate_behaviour=False, timeout=timeout)

        self.last_x, self.last_y = x, y

    def down(self, button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float], emulate_behaviour: Optional[bool] = True, timeout: Optional[float] = None) -> None:
        x, y = int(x), int(y)

        if self.emulate_behaviour and emulate_behaviour:
            self.move(x=x, y=y, emulate_behaviour=emulate_behaviour, timeout=timeout)
        self._base.down(button=button, x=x, y=y)
        self.last_x, self.last_y = x, y

    def up(self, button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float]) -> None:
        x, y = int(x), int(y)

        self._base.up(button=button, x=x, y=y)
        self.last_x, self.last_y = x, y

    def move(self, x: Union[int, float], y: Union[int, float], emulate_behaviour: Optional[bool] = True, timeout: Optional[float] = None) -> None:
        x, y = int(x), int(y)

        if self.emulate_behaviour and emulate_behaviour:
            humanized_points = HumanizeMouseTrajectory((self.last_x, self.last_y), (x, y))

            # Move Mouse to new random locations
            for i, (human_x, human_y) in enumerate(humanized_points.points):
                self._base.move(x=int(human_x), y=int(human_y))
                self._sleep_timeout(timeout=timeout)

        self._base.move(x=x, y=y)
        self.last_x, self.last_y = x, y

    def scroll(self, direction: Literal["up", "down", "left", "right"], amount: int) -> None:
        warnings.warn("Scrolling using CDP-Patches is discouraged as Scroll Inputs dont leak the CDP Domain.", UserWarning)
        self._base.scroll(direction=direction, amount=amount)

    def type(self, text: str, fill: Optional[bool] = False, timeout: Optional[float] = None) -> None:
        if self.emulate_behaviour and not fill:
            for i, char in enumerate(self.selective_modifiers_regex.findall(text)):
                # If new word is started wait some more time
                if i != 0 and text[i - 1] == " ":
                    self._sleep_timeout(timeout=timeout)

                self._base.send_keystrokes(char)
                self._sleep_timeout((random.random() * 10) / self.typing_speed)
        else:
            self._base.send_keystrokes(text)
