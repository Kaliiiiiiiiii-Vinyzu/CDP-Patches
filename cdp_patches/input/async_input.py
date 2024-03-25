from __future__ import annotations

import asyncio
import os
import random
import re
import threading
import time
from typing import Any, Generator, Literal, Optional, Union

from pywinauto.base_wrapper import ElementNotEnabled, ElementNotVisible

from cdp_patches.input.os_base.windows import WindowsBase

from .browsers import async_browsers, get_async_browser_pid, get_async_scale_factor
from .mouse_trajectory import HumanizeMouseTrajectory


class AsyncInput:
    emulate_behaviour: Optional[bool] = True
    pid: Optional[int]
    _base: Union[WindowsBase]
    window_timeout: int = 30
    _scale_factor: float = 1.0
    timeout: float = 0.01
    typing_speed: int = 50
    last_x: int = 0
    last_y: int = 0
    selective_modifiers_regex = re.compile(r"{[^{}]*}|.")

    def __init__(self, pid: Optional[int] = None, browser: Optional[async_browsers] = None, scale_factor: Optional[float] = 1.0, emulate_behaviour: Optional[bool] = True) -> None:
        self.pid = pid
        self.browser = browser
        self._scale_factor = scale_factor or self._scale_factor
        self.emulate_behaviour = emulate_behaviour or self.emulate_behaviour

    def __await__(self) -> Generator[None, Any, AsyncInput]:
        yield from self.__ainit__().__await__()
        return self

    async def __ainit__(self) -> None:
        if self.browser:
            self.pid = await get_async_browser_pid(self.browser)
            self._scale_factor = await get_async_scale_factor(self.browser)
        elif not self.pid:
            raise ValueError("You must provide a pid or a browser")

        if os.name == "nt":
            self._base = WindowsBase(self.pid, self._scale_factor)
        else:
            # mind to change typing of `self.base` property when implementing
            raise NotImplementedError(f"pyinput not implemented yet for {os.name}")
        await self._wait_for_window()

        self._base._offset_toolbar_height()

    @property
    def base(self) -> WindowsBase:
        return self._base

    @property
    def scale_factor(self) -> float:
        return self._scale_factor

    @scale_factor.setter
    def scale_factor(self, scale_value: float) -> None:
        self._scale_factor = scale_value
        if self._base:
            self._base.scale_factor = scale_value

    async def _wait_for_window(self) -> None:
        max_wait = time.time() + self.window_timeout
        while time.time() < max_wait:
            try:
                if self._base.get_window():
                    return
            except (AssertionError, ElementNotVisible, ElementNotEnabled):
                pass
            await self._sleep_timeout(0.1)

        raise TimeoutError(f"Chrome Window (PID: {self.pid}) not found in {self.window_timeout} seconds.")

    async def _sleep_timeout(self, timeout: Optional[float] = None) -> None:
        timeout = timeout or self.timeout
        if not random.randint(0, 10):
            timeout_random = self.timeout / 10
            timeout = timeout or random.uniform(self.timeout, self.timeout + timeout_random)

        await asyncio.sleep(timeout)

    async def click(self, button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float], emulate_behaviour: Optional[bool] = True, timeout: Optional[float] = None) -> None:
        x, y = int(x), int(y)

        await self.down(button=button, x=x, y=y, emulate_behaviour=emulate_behaviour, timeout=timeout)
        if self.emulate_behaviour and emulate_behaviour:
            await self._sleep_timeout(timeout=timeout)
        await self.up(button=button, x=x, y=y)
        self.last_x, self.last_y = x, y

    async def double_click(self, button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float], emulate_behaviour: Optional[bool] = True, timeout: Optional[float] = None) -> None:
        x, y = int(x), int(y)

        await self.click(button=button, x=x, y=y, timeout=timeout, emulate_behaviour=emulate_behaviour)
        if self.emulate_behaviour and emulate_behaviour:
            # self._sleep_timeout(random.uniform(0.14, 0.21))
            await self._sleep_timeout(timeout=timeout)
        await self.click(button=button, x=x, y=y, emulate_behaviour=False, timeout=timeout)

        self.last_x, self.last_y = x, y

    async def down(self, button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float], emulate_behaviour: Optional[bool] = True, timeout: Optional[float] = None) -> None:
        x, y = int(x), int(y)

        if self.emulate_behaviour and emulate_behaviour:
            await self.move(x=x, y=y, timeout=timeout, emulate_behaviour=emulate_behaviour)
        self._base.down(button=button, x=x, y=y)
        self.last_x, self.last_y = x, y

    async def up(self, button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float]) -> None:
        x, y = int(x), int(y)

        self._base.up(button=button, x=x, y=y)
        self.last_x, self.last_y = x, y

    async def move(self, x: Union[int, float], y: Union[int, float], emulate_behaviour: Optional[bool] = True, timeout: Optional[float] = None) -> None:
        x, y = int(x), int(y)

        if self.emulate_behaviour and emulate_behaviour:
            humanized_points = HumanizeMouseTrajectory((self.last_x, self.last_y), (x, y))

            # Move Mouse to new random locations
            for human_x, human_y in humanized_points.points:
                # Threaded Movement as Calls to API are too slow
                threading.Thread(target=self._base.move, args=(int(human_x), int(human_y))).start()
                await self._sleep_timeout(timeout=timeout)

        else:
            self._base.move(x=x, y=y)
        self.last_x, self.last_y = x, y

    async def scroll(self, direction: Literal["up", "down", "left", "right"], amount: int) -> None:
        self._base.scroll(direction=direction, amount=amount)

    async def type(self, text: str, fill: Optional[bool] = False) -> None:
        if self.emulate_behaviour and not fill:
            for i, char in enumerate(self.selective_modifiers_regex.findall(text)):
                # If new word is started wait some more time
                if i != 0 and text[i - 1] == " ":
                    await self._sleep_timeout()

                self._base.send_keystrokes(char)
                await self._sleep_timeout((random.random() * 10) / self.typing_speed)
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
