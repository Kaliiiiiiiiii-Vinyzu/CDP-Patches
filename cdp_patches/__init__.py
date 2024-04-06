import platform

VERSION = 1.0

system_name = platform.system()
if system_name == "Windows":
    is_windows = True
elif system_name == "Linux":
    is_windows = False
else:
    raise SystemError("Unknown system (You´re probably using MacOS, which is currently not supported).")

__all__ = ["VERSION", "is_windows"]
