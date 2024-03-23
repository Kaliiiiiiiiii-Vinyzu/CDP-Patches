# CDP-Patches v1.0
![CDP-Patches CI](https://github.com/Kaliiiiiiiiii-Vinyzu/CDP-Patches/actions/workflows/ci.yml/badge.svg)
[![](https://img.shields.io/pypi/v/cdp-patches.svg?color=1182C3)](https://pypi.org/project/cdp-patches/)
[![Downloads](https://static.pepy.tech/badge/cdp-patches)](https://pepy.tech/project/cdp-patches)

## Install it from PyPI

```bash
pip install cdp-patches
```

---

# Leaks
### Concept: Input Domain Leaks
Bypass CDP Leaks in [Input](https://chromedevtools.github.io/devtools-protocol/tot/Input/) domains

For an interaction event `e`, the page coordinates won't ever equal the screen coordinates, unless Chrome is in fullscreen.
However, all `CDP` input commands just set it the same by default (see [crbug#1477537](https://bugs.chromium.org/p/chromium/issues/detail?id=1477537)).
```js
var is_bot = (e.pageY == e.screenY && e.pageX == e.screenX)
if (is_bot && 1 >= outerHeight - innerHeight){ // fullscreen
    is_bot = false
}
```

Furthermore, CDP can't dispatch `CoalescedEvent`'s ([demo](https://omwnk.codesandbox.io/)).

As we don't want to patch Chromium itsself, let's just dispatch this event at OS-level!

---

## Usage

```py
from cdp_patches.input import SyncInput

sync_input = SyncInput(pid=pid)
# Or
sync_input = SyncInput(browser=browser)

# Dispatch Inputs
sync_input.click("left", 100, 100)  # Left click at (100, 100)
sync_input.double_click("left", 100, 100)  # Left double-click at (100, 100)
sync_input.down("left", 100, 100)  # Left mouse button down at (100, 100)
sync_input.up("left", 100, 100)  # Left mouse button up at (100, 100)
sync_input.move(100, 100)  # Move mouse to (100, 100)
sync_input.scroll("down", 10)  # Scroll down by 10 lines
sync_input.type("Hello World!")  # Type "Hello World!"
```

## Async Usage

```py
import asyncio

from cdp_patches.input import AsyncInput

async def main():
    async_input = await AsyncInput(pid=pid)
    # Or
    async_input = await AsyncInput(browser=browser)
    
    # Dispatch Inputs
    await async_input.click("left", 100, 100)  # Left click at (100, 100)
    await async_input.double_click("left", 100, 100)  # Left double-click at (100, 100)
    await async_input.down("left", 100, 100)  # Left mouse button down at (100, 100)
    await async_input.up("left", 100, 100)  # Left mouse button up at (100, 100)
    await async_input.move(100, 100)  # Move mouse to (100, 100)
    await async_input.scroll("down", 10)  # Scroll down by 10 lines
    await async_input.type("Hello World!")  # Type "Hello World!"

if __name__ == '__main__':
    asyncio.run(main())
```

> [!IMPORTANT]  
> Because Chrome does not recognize Input Events to specific tabs, these methods can only be used on the active tab. 
> Chrome Tabs do have their own process with a process id (pid), but these can not be controlled using Input Events as they´re just engines.


Read the [Documentation](https://github.com/Kaliiiiiiiiii-Vinyzu/CDP-Patches/blob/main/docs/index.rst)

---

## Development

Read the [CONTRIBUTING.md](https://github.com/Vinyzu/Botright/blob/main/docs/CONTRIBUTING.md) file.

---

## Copyright and License
© [Vinyzu](https://github.com/Vinyzu/)

[GNU GPL](https://choosealicense.com/licenses/gpl-3.0/)

(Commercial Usage is allowed, but source, license and copyright has to made available. Botright does not provide and Liability or Warranty)

---

## Authors

[Vinyzu](https://github.com/Vinyzu/), 
[Kaliiiiiiiiii](https://github.com/kaliiiiiiiiii/)

---

![Version](https://img.shields.io/badge/CDP_Patches-v1.0-blue)
![License](https://img.shields.io/badge/License-GNU%20GPL-green)
![Python](https://img.shields.io/badge/Python-v3.x-lightgrey)
