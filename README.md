<h1 align="center">
    CDP-Patches v1.0
</h1>


<p align="center">
    <a href="https://github.com/Kaliiiiiiiiii-Vinyzu/CDP-Patches/blob/main/LICENSE">
        <img src="https://img.shields.io/badge/License-GNU%20GPL-green">
    </a>
    <a href="https://python.org/">
        <img src="https://img.shields.io/badge/python-3.9&#8208;3.12-blue">
    </a>
    <a href="https://pypi.org/project/cdp-patches/">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/cdp-patches.svg?color=1182C3">
    </a>
    <a href="https://pepy.tech/project/cdp-patches">
        <img alt="PyPI" src="https://static.pepy.tech/badge/cdp-patches">
    </a>
    <br>
    <a href="https://github.com/Kaliiiiiiiiii-Vinyzu/CDP-Patches/actions">
        <img src="https://github.com/Kaliiiiiiiiii-Vinyzu/CDP-Patches/actions/workflows/ci.yml/badge.svg">
    </a>
    <a href="http://mypy-lang.org">
        <img src="http://www.mypy-lang.org/static/mypy_badge.svg">
    </a>
    <a href="https://github.com/PyCQA/flake8">
        <img src="https://img.shields.io/badge/code%20quality-Flake8-green.svg">
    </a>
    <a href="https://github.com/ambv/black">
        <img src="https://img.shields.io/badge/code%20style-black-black.svg">
    </a>
    <a href="https://github.com/PyCQA/isort">
        <img src="https://img.shields.io/badge/imports-isort-yellow.svg">
    </a>
</p>

## Install it from PyPI

```bash
pip install cdp-patches
```
<details>
    <summary>Or for Full Linting</summary>

#### (Includes: playwright, botright, selenium, selenium_driverless)
```bash
pip install cdp-patches[automation_linting]
```
</details>

---

# Leak Patches
<details>
    <summary>Input Package</summary>

###  Concept: Input Domain Leaks
Bypass CDP Leaks in [Input](https://chromedevtools.github.io/devtools-protocol/tot/Input/) domains

[![Brotector Banner](https://github.com/Kaliiiiiiiiii-Vinyzu/CDP-Patches/assets/50874994/fdbe831d-cb39-479d-ba0a-fea7f29fe90a)](https://github.com/kaliiiiiiiiii/brotector)

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

### TODO
- [ ] Improve mouse movement timings.
- [ ] Implement extensive testing.

#### Owner: [Vinyzu](https://github.com/Vinyzu/)
#### Co-Maintainer: [Kaliiiiiiiiii](https://github.com/kaliiiiiiiiii/)
</details>


> [!IMPORTANT]  
> By the nature of OS-level events (which can only impact actionable windows), this package can only be used with headful browsers.

> [!WARNING]  
> Pressing `SHIFT` or `CAPSLOCK` manually on Windows affects `input.type(text) as well.`

> [!WARNING]  
> Because Chrome does not recognize Input Events to specific tabs, these methods can only be used on the active tab. 
> Chrome Tabs do have their own process with a process id (pid), but these can not be controlled using Input Events as they´re just engines.


Read the [Documentation](https://vinyzu.gitbook.io/cdp-patches-documentation)

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