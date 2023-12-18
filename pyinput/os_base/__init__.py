class BaseInput:
    def __init__(self, hwnd: str) -> None:
        self._hwnd = hwnd

    @property
    def hwnd(self):
        return self._hwnd


class Pointer:
    LEFT = "l"
    RIGHT = "r"
