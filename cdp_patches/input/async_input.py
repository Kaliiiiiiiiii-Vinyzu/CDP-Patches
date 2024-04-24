from __future__ import annotations

import asyncio
import platform
import random
import re
import sys
import time
from typing import Any, Generator, Literal, Optional, Union

if sys.version_info.minor >= 10:
    from typing import TypeAlias
else:
    TypeAlias = "TypeAlias"  # type: ignore[assignment]

from cdp_patches import is_windows
from cdp_patches.input.exceptions import WindowClosedException

if is_windows:
    from pywinauto.application import ProcessNotFoundError
    from pywinauto.base_wrapper import ElementNotEnabled

    from cdp_patches.input.os_base.windows import WindowsBase  # type: ignore[assignment]

    LinuxBase: TypeAlias = WindowsBase  # type: ignore[no-redef]
    InputBase = WindowsBase  # type: ignore
    WindowErrors = (ValueError, ElementNotEnabled, ProcessNotFoundError, WindowClosedException)  # type: ignore[assignment]
else:
    from cdp_patches.input.os_base.linux import LinuxBase  # type: ignore[assignment]

    WindowsBase: TypeAlias = LinuxBase  # type: ignore[no-redef]
    InputBase = LinuxBase  # type: ignore
    WindowErrors = (AssertionError, ValueError, WindowClosedException)  # type: ignore[assignment]

from .browsers import DriverlessAsyncChrome, async_browsers, get_async_browser_pid, get_async_scale_factor
from .mouse_trajectory import HumanizeMouseTrajectory


class AsyncInput:
    emulate_behaviour: Optional[bool] = True
    pid: Optional[int]
    _base: Union[WindowsBase, LinuxBase]
    window_timeout: float = 30.0
    _scale_factor: float = 1.0
    sleep_timeout: float = 0.01
    typing_speed: int = 50
    last_x: int = 0
    last_y: int = 0
    selective_modifiers_regex = re.compile(r"{[^{}]*}|.")

    def __init__(
        self, pid: Optional[int] = None, browser: Optional[async_browsers] = None, scale_factor: Optional[float] = 1.0, emulate_behaviour: Optional[bool] = True, window_timeout: Optional[float] = 30.0
    ) -> None:
        if platform.system() not in ('Windows', 'Linux'):
            raise SystemError("Unknown system (You´re probably using MacOS, which is currently not supported).")

        self.pid = pid
        self.browser = browser
        self.window_timeout = window_timeout or self.window_timeout
        self._scale_factor = scale_factor or self._scale_factor
        self.emulate_behaviour = emulate_behaviour or self.emulate_behaviour
        self._move_lock = asyncio.Lock()

    def __await__(self) -> Generator[None, Any, AsyncInput]:
        yield from self.__ainit__().__await__()
        return self

    async def __ainit__(self) -> None:
        if self.browser:
            self.pid = await get_async_browser_pid(self.browser)
            self._scale_factor = float(await get_async_scale_factor(self.browser))
        elif not self.pid:
            raise ValueError("You must provide a pid or a browser")

        self._base = InputBase(self.pid, self._scale_factor)  # type: ignore
        await self._wait_for_window()

        # Include Windows Scale Factor for every browser except DriverlessSyncChrome
        if is_windows and not isinstance(self.browser, DriverlessAsyncChrome):
            self._base.include_windows_scale_factor()

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

    async def _wait_for_window(self) -> None:
        max_wait = time.perf_counter() + self.window_timeout
        while time.perf_counter() < max_wait:
            try:
                if await self.base.async_get_window():
                    return
            except WindowErrors:
                pass
            await self._sleep_timeout(0.1)

        raise TimeoutError(f"Chrome Window (PID: {self.pid}) not found in {self.window_timeout} seconds.")

    async def _sleep_timeout(self, timeout: Optional[float] = None) -> None:
        timeout = timeout or self.sleep_timeout
        if not random.randint(0, 10):
            timeout_random = self.sleep_timeout / 10
            timeout = timeout or random.uniform(self.sleep_timeout, self.sleep_timeout + timeout_random)

        await asyncio.sleep(timeout)

    async def click(self, button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float], emulate_behaviour: Optional[bool] = True, timeout: Optional[float] = None) -> None:
        x, y = int(x), int(y)

        await self.down(button=button, x=x, y=y, emulate_behaviour=emulate_behaviour, timeout=timeout)
        if self.emulate_behaviour and emulate_behaviour:
            await self._sleep_timeout(timeout=timeout)
        await self.up(button=button, x=x, y=y)
        self.last_x, self.last_y = x, y

    async def double_click(
        self, button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float], emulate_behaviour: Optional[bool] = True, timeout: Optional[float] = None
    ) -> None:
        x, y = int(x), int(y)

        await self.click(button=button, x=x, y=y, timeout=timeout, emulate_behaviour=emulate_behaviour)
        if self.emulate_behaviour and emulate_behaviour:
            await self._sleep_timeout(random.uniform(0.14, 0.21))
            # await self._sleep_timeout(timeout=timeout)
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
        async with self._move_lock:
            x, y = int(x), int(y)

            if self.emulate_behaviour and emulate_behaviour:
                humanized_points = HumanizeMouseTrajectory((self.last_x, self.last_y), (x, y))

                # Move Mouse to new random locations
                for i, (human_x, human_y) in enumerate(humanized_points.points):
                    self._base.move(x=int(human_x), y=int(human_y))
                    await self._sleep_timeout(timeout=timeout)

            else:
                self._base.move(x=x, y=y)
            self.last_x, self.last_y = x, y

    async def scroll(self, direction: Literal["up", "down", "left", "right"], amount: int) -> None:
        self._base.scroll(direction=direction, amount=amount)

    async def type(self, text: str, fill: Optional[bool] = False, timeout: Optional[float] = None) -> None:
        if self.emulate_behaviour and not fill:
            for i, char in enumerate(self.selective_modifiers_regex.findall(text)):
                # If new word is started wait some more time
                if i != 0 and text[i - 1] == " ":
                    await self._sleep_timeout(timeout=timeout)

                self._base.send_keystrokes(char)
                await self._sleep_timeout((random.random() * 10) / self.typing_speed)
        else:
            self._base.send_keystrokes(text)
