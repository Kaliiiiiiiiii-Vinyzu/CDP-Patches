from pyinput.base import NormPointer
from pyinput.os_base import Pointer
import time


class BasePointer(NormPointer):
    def click(self, x: int, y: int, timeout: float = 0.01, button: str = Pointer.LEFT):
        self.down(x, y, button=button)
        time.sleep(timeout)
        self.up(x, y, button=button)

    def db_click(self, x: int, y: int, timeout: float = 0.01, button: str = Pointer.LEFT):
        self.click(x, y, timeout=timeout, button=button)
        time.sleep(timeout)
        self.click(x, y, timeout=timeout, button=button)
