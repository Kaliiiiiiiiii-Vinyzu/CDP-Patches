from typing import Optional

from cdp_patches import is_windows


def _mk_kwargs(pressed: Optional[str]) -> dict[str, str]:
    kwargs = {}
    if pressed is not None:
        if not is_windows:
            raise NotImplementedError("specifying pressed buttons currently only supported for windows")
        kwargs["pressed"] = pressed
    return kwargs
