import os
import socket
import sys
from contextlib import closing
from typing import Optional

IS_POSIX = sys.platform.startswith(("darwin", "cygwin", "linux", "linux2"))


def find_chrome_executable() -> str:
    """
    Finds the Chrome, Chrome beta, Chrome canary, Chromium executable

    Returns
    -------
    executable_path :  str
        the full file path to found executable

    """
    candidates = set()
    if IS_POSIX:
        for posix_item in os.environ.get("PATH", "").split(os.pathsep):
            for subitem in (
                "google-chrome",
                "chromium",
                "chromium-browser",
                "chrome",
                "google-chrome-stable",
            ):
                candidates.add(os.sep.join((posix_item, subitem)))
        if "darwin" in sys.platform:
            candidates.update(
                [
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "/Applications/Chromium.app/Contents/MacOS/Chromium",
                ]
            )
    else:
        for windows_item in map(
            os.environ.get,
            ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA", "PROGRAMW6432"),
        ):
            if windows_item is not None:
                for subitem in (
                    "Google/Chrome/Application",
                    "Google/Chrome Beta/Application",
                    "Google/Chrome Canary/Application",
                ):
                    candidates.add(os.sep.join((windows_item, subitem, "chrome.exe")))
    for candidate in candidates:
        if os.path.exists(candidate) and os.access(candidate, os.X_OK):
            return os.path.normpath(candidate)
    raise FileNotFoundError("Couldn't find installed Chrome or Chromium executable")


def random_port(host: Optional[str] = "") -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind((host, 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return int(s.getsockname()[1])
