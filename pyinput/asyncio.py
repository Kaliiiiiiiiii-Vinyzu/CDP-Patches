import asyncio

from pyinput.base import NormPointer
from pyinput.os_base import Pointer


class BasePointer(NormPointer):
    async def click(self, x: int, y: int, timeout: float = 0.01, button: str = Pointer.LEFT):
        self.down(x, y, button=button)
        await asyncio.sleep(timeout)
        self.up(x, y, button=button)

    async def db_click(self, x: int, y: int, timeout: float = 0.01, button: str = Pointer.LEFT):
        await self.click(x, y, timeout=timeout, button=button)
        await asyncio.sleep(timeout)
        await self.click(x, y, timeout=timeout, button=button)
