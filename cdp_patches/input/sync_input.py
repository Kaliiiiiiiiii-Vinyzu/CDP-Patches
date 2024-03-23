import os
import random
import re
import threading
import time
from typing import Literal, Optional, Union

from pywinauto.base_wrapper import ElementNotEnabled, ElementNotVisible

from cdp_patches.input.os_base.windows import WindowsBase

from .browsers import get_sync_browser_pid, get_sync_scale_factor, sync_browsers
from .mouse_trajectory import HumanizeMouseTrajectory


class SyncInput:
    emulate_behaviour: Optional[bool] = True
    pid: Optional[int]
    _base: Union[WindowsBase]
    window_timeout: int = 30
    scale_factor: float = 1.0
    timeout: float = 0.01
    typing_speed: int = 50
    last_x: int = 0
    last_y: int = 0
    selective_modifiers_regex = re.compile(r"{[^{}]*}|.")

    def __init__(self, pid: Optional[int] = None, browser: Optional[sync_browsers] = None, scale_factor: Optional[float] = 1.0, emulate_behaviour: Optional[bool] = True) -> None:
        self.scale_factor = scale_factor or self.scale_factor
        self.emulate_behaviour = emulate_behaviour or self.emulate_behaviour

        if browser:
            self.pid = get_sync_browser_pid(browser)
            self.scale_factor = get_sync_scale_factor(browser)
        elif pid:
            self.pid = pid
        else:
            raise ValueError("You must provide a pid or a browser")

        if os.name == "nt":
            self._base = WindowsBase(self.pid, self.scale_factor)
        else:
            raise NotImplementedError(f"pyinput not implemented yet for {os.name}")
        self._wait_for_window()

        self._base._offset_toolbar_height()

    def _wait_for_window(self) -> None:
        max_wait = time.time() + self.window_timeout
        while time.time() < max_wait:
            try:
                if self._base.get_window():
                    return
            except (AssertionError, ElementNotVisible, ElementNotEnabled):
                pass
            self._sleep_timeout(0.1)

        raise TimeoutError(f"Chrome Window (PID: {self.pid}) not found in {self.window_timeout} seconds.")

    def _sleep_timeout(self, timeout: Optional[float] = None) -> None:
        timeout = timeout or self.timeout
        if not random.randint(0, 10):
            timeout_random = self.timeout / 10
            timeout = timeout or random.uniform(self.timeout, self.timeout + timeout_random)

        time.sleep(timeout)

    def click(self, button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float]) -> None:
        x, y = int(x), int(y)

        self.down(button=button, x=x, y=y)
        if self.emulate_behaviour:
            self._sleep_timeout()
        self.up(button=button, x=x, y=y)
        self.last_x, self.last_y = x, y

    def double_click(self, button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float]) -> None:
        x, y = int(x), int(y)
        emulate_behaviour = self.emulate_behaviour

        self.click(button=button, x=x, y=y)
        if self.emulate_behaviour:
            # self._sleep_timeout(random.uniform(0.14, 0.21))
            self._sleep_timeout()
        self.emulate_behaviour = False
        self.click(button=button, x=x, y=y)

        self.emulate_behaviour = emulate_behaviour
        self.last_x, self.last_y = x, y

    def down(self, button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float]) -> None:
        x, y = int(x), int(y)

        if self.emulate_behaviour:
            self.move(x=x, y=y)
        self._base.down(button=button, x=x, y=y)
        self.last_x, self.last_y = x, y

    def up(self, button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float]) -> None:
        x, y = int(x), int(y)

        self._base.up(button=button, x=x, y=y)
        self.last_x, self.last_y = x, y

    def move(self, x: Union[int, float], y: Union[int, float]) -> None:
        x, y = int(x), int(y)

        if self.emulate_behaviour:
            humanized_points = HumanizeMouseTrajectory((self.last_x, self.last_y), (x, y))

            # Move Mouse to new random locations
            for human_x, human_y in humanized_points.points:
                # Threaded Movement as Calls to API are too slow
                threading.Thread(target=self._base.move, args=(int(human_x), int(human_y))).start()
                self._sleep_timeout()

        self._base.move(x=x, y=y)
        self.last_x, self.last_y = x, y

    def scroll(self, direction: Literal["up", "down", "left", "right"], amount: int) -> None:
        self._base.scroll(direction=direction, amount=amount)

    def type(self, text: str, fill: Optional[bool] = False) -> None:
        if self.emulate_behaviour and not fill:
            for i, char in enumerate(self.selective_modifiers_regex.findall(text)):
                # If new word is started wait some more time
                if i != 0 and text[i - 1] == " ":
                    self._sleep_timeout()

                self._base.send_keystrokes(char)
                self._sleep_timeout((random.random() * 10) / self.typing_speed)
        else:
            self._base.send_keystrokes(text)

    # async def press_keys(self, text: str, fill: Optional[bool] = False) -> None:
    #     if self.emulate_behaviour and not fill:
    #         for i, char in enumerate(self.selective_modifiers_regex.findall(text)):
    #             # If new word is started wait some more time
    #             if i != 0 and text[i - 1] == " ":
    #                 await self._sleep_timeout()
    #
    #             self._base.send_keystrokes(char, down=True)
    #             await self._sleep_timeout((random.random() * 10) / self.typing_speed)
    #     else:
    #         self._base.send_keystrokes(text)
    #
    # async def release_keys(self, text: str, fill: Optional[bool] = False) -> None:
    #     if self.emulate_behaviour and not fill:
    #         for i, char in enumerate(self.selective_modifiers_regex.findall(text)):
    #             # If new word is started wait some more time
    #             if i != 0 and text[i - 1] == " ":
    #                 await self._sleep_timeout()
    #
    #             self._base.send_keystrokes(char, up=True)
    #             await self._sleep_timeout((random.random() * 10) / self.typing_speed)
    #     else:
    #         self._base.send_keystrokes(text)
