class BasePointer:
    def __init__(self) -> None:
        raise NotImplementedError()

    def down(self, x, y):
        raise NotImplementedError()

    def up(self, x, y):
        raise NotImplementedError()


class BaseKeyBoard:
    def __init__(self) -> None:
        raise NotImplementedError()


class BaseTouch:
    def __init__(self) -> None:
        raise NotImplementedError()
