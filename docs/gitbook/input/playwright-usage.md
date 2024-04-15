# Playwright Usage



## Sync Usage (Sync Playwright)

```python
from playwright.sync_api import sync_playwright
from cdp_patches.input import SyncInput

# Locator Position Helper
def get_locator_pos(locator: Locator):
    bounding_box = locator.bounding_box()
    assert bounding_box

    x, y, width, height = bounding_box.get("x"), bounding_box.get("y"), bounding_box.get("width"), bounding_box.get("height")
    assert x and y and width and height

    x, y = x + width // 2, y + height // 2
    return x, y

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    page = browser.new_page()
    sync_input = SyncInput(browser=browser)  # Also works with Contexts

    # Example: Click Button
    # Find Button Coords
    locator = page.locator("button")
    x, y = get_locator_pos(locator)
    # Click Coords => Click Button
    sync_input.click("left", x, y)
```

## Async Usage (Async Playwright / Botright)

```python
from playwright.async_api import async_playwright
from cdp_patches.input import AsyncInput

# Locator Position Helper
async def get_locator_pos(locator: WebElement):
    location = await locator.location
    size = await locator.size
    assert location, size

    x, y, width, height = location.get("x"), location.get("y"), size.get("width"), size.get("height")
    assert x and y and width and height

    x, y = x + width // 2, y + height // 2
    return x, y

async with async_playwright() as playwright:
    browser = await playwright.chromium.launch()
    page = await browser.new_page()
    async_input = await AsyncInput(browser=browser)  # Also works with Contexts

    # Example: Click Button
    # Find Button Coords
    locator = page.locator("button")
    x, y = await get_locator_pos(locator)
    # Click Coords => Click Button
    await async_input.click("left", x, y)
```
