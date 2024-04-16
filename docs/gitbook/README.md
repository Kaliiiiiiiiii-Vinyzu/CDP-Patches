---
description: Welcome to CDP-Patches!
---

# Installation



## Install it from PyPI [![PyPI version](https://img.shields.io/pypi/v/cdp-patches.svg)](https://pypi.org/project/cdp-patches/)

```bash
pip install cdp-patches
```

<details>

<summary>Or for Full Linting</summary>

#### (Includes: playwright, botright, selenium, selenium\_driverless)

```bash
pip install cdp-patches[automation_linting]
```

</details>

***

## Leak Patches

<details>

<summary>Input Package</summary>

## First Script

### Sync Usage

```python
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
sync_input.type("Hello World!")  # Type "Hello WorldS
```

[sync-usage.md](input/sync-usage.md "mention")

***

### Async Usage

```python
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

[async-usage.md](input/async-usage.md "mention")

***

### Usage with Selenium

[selenium-usage.md](input/selenium-usage.md "mention")

### Usage with Playwright

[playwright-usage.md](input/playwright-usage.md "mention")

</details>

