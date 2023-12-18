import os
import typing

from pyinput.os_base import Pointer
from pyinput.os_base.linux import BasePointer as BaseLinuxPointer
from pyinput.os_base.windows import BasePointer as BaseWinPointer


class NormPointer:
    def __init__(self, hwnd: str, scale_factor: float):
        if os.name == 'nt':
            self._base = BaseWinPointer(hwnd, scale_factor)
        else:
            raise NotImplementedError(f"pyinput not implemented yet for {os.name}")

    def down(self, x: float, y: float, button: str = Pointer.LEFT):
        return self.base.down(x, y, button)

    def up(self, x: float, y: float, button: str = Pointer.LEFT):
        return self.base.up(x, y, button)

    @property
    def scale_factor(self):
        return self.base.scale_factor

    @scale_factor.setter
    def scale_factor(self, factor: float):
        self.base.scale_factor = factor

    @property
    def base(self) -> typing.Union[BaseWinPointer, BaseLinuxPointer]:
        return self._base


class BaseKeyBoard:
    def __init__(self):
        raise NotImplementedError()


class BaseTouch:
    def __init__(self) -> None:
        raise NotImplementedError()
