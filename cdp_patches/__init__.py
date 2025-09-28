import platform
import warnings

VERSION = "1.1"

warnings.warn(
    """
    The [crbug#1477537](https://bugs.chromium.org/p/chromium/issues/detail?id=1477537) causing the Input Leak has been fixed in [#6917162](https://chromium-review.googlesource.com/c/chromium/src/+/6917162). It will probably be implemented in Chrome-Stable v142+. <br>
    CoalescedEvents are now also emitted by Input Events. There is no reason to use this package anymore, except for Select Elements ([crbug#40943840](https://issues.chromium.org/issues/40943840)). 
    """,
    DeprecationWarning,
)

system_name = platform.system()
if system_name == "Windows":
    is_windows = True
elif system_name == "Linux":
    is_windows = False
else:
    is_windows = False
    warnings.warn(
        "Unknown system (You´re probably using MacOS, which is currently not supported).",
        RuntimeWarning,
    )

__all__ = ["VERSION", "is_windows"]
