from ctypes import pointer
import win32gui, win32con, win32api
from pyinput.os_base import BaseInput, Pointer


class BasePointer(BaseInput):
    def __init__(self, hwnd: str, scale_factor: float):
        self._scale_factor = scale_factor
        super().__init__(hwnd)

    def _make_long(self, x: float, y: float):
        # noinspection PyUnresolvedReferences
        return win32api.MAKELONG(int(x * self.scale_factor), int(y * self.scale_factor))

    def down(self, x: float, y: float, button: str = Pointer.LEFT):
        if button == Pointer.LEFT:
            msg = win32con.WM_LBUTTONDOWN
            wparam = win32con.MK_LBUTTON
        elif button == Pointer.RIGHT:
            msg = win32con.WM_RBUTTONDOWN
            wparam = win32con.MK_RBUTTON
        else:
            raise ValueError(f"expected Pointer.*****, but got: {button}")
        lparam = self._make_long(x, y)
        return win32gui.PostMessage(self.hwnd, msg, wparam, lparam)

    def up(self, x: float, y: float, button: str = Pointer.LEFT):
        if button == Pointer.LEFT:
            msg = win32con.WM_LBUTTONUP
            wparam = win32con.MK_LBUTTON
        elif button == Pointer.RIGHT:
            msg = win32con.WM_RBUTTONUP
            wparam = win32con.MK_RBUTTON
        else:
            raise ValueError(f"expected Pointer.*****, but got: {button}")
        lparam = self._make_long(x, y)
        return win32gui.PostMessage(self.hwnd, msg, None, lparam)

    @property
    def scale_factor(self):
        return self._scale_factor

    @scale_factor.setter
    def scale_factor(self, factor: float):
        self._scale_factor = factor


class BaseKeyBoard(BaseInput):
    @staticmethod
    def _make_key(scan_code: int, repeat_count: int = 0,
                  extended: bool = False, context_code: int = 0,
                  prev_state: 0 | 1 = 0, transition: int = 0):
        if extended:
            extended = 1
        else:
            extended = 0
        return repeat_count \
            | (scan_code << 16) \
            | (extended << 24) \
            | (context_code << 29) \
            | (prev_state << 30) \
            | (transition << 31)

    def down(self, vkey: int, scan_code: int, repeat_count: int = 0,
             extended: bool = False, context_code: int = 0,
             prev_state: 0 | 1 = 0):
        lparam = self._make_key(scan_code=scan_code, repeat_count=repeat_count,
                                extended=extended, context_code=context_code,
                                prev_state=prev_state, transition=0)
        return win32gui.PostMessage(self.hwnd, win32con.WM_KEYDOWN, vkey, lparam)

    def up(self, vkey: int, scan_code: int, repeat_count: int = 0,
           extended: bool = False, context_code: int = 0):
        lparam = self._make_key(scan_code=scan_code, repeat_count=repeat_count,
                                extended=extended, context_code=context_code,
                                prev_state=1, transition=1)
        return win32gui.PostMessage(self.hwnd, win32con.WM_KEYUP, vkey, lparam)


class BaseTouch:
    def __init__(self) -> None:
        raise NotImplementedError()
