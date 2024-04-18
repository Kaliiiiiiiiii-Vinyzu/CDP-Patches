from typing import Optional


class WindowClosedException(Exception):
    def __init__(self, message: Optional[str] = None, pid: Optional[int] = None):
        if not message:
            if pid:
                message = f"Interaction not possible due to stale/closed window with pid {pid}"
            else:
                message = "Interaction not possible due to stale/closed window"

        super().__init__(message)
