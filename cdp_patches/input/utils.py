from typing import Union
from cdp_patches import is_windows


def _mk_kwargs(pressed: Union[str, None]) -> dict:
    kwargs = {}
    if pressed is not None:
        if not is_windows:
            raise NotImplementedError("specifying pressed buttons currently only supported for windows")
        kwargs["pressed"] = pressed
    return kwargs
