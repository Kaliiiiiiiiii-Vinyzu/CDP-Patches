import platform
import warnings

VERSION = "1.1"

system_name = platform.system()
if system_name == "Windows":
    is_windows = True
elif system_name == "Linux":
    is_windows = False
else:
    is_windows = False
    warnings.warn("Unknown system (You´re probably using MacOS, which is currently not supported).", RuntimeWarning)

__all__ = ["VERSION", "is_windows"]
