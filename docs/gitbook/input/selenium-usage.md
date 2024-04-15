# Selenium Usage



## Sync Usage (Selenium / Sync Selenium-Driverless)

```python
from selenium import webdriver
from cdp_patches.input import SyncInput

# Locator Position Helper
def get_locator_pos(locator: WebElement):
    location = locator.location
    size = locator.size
    assert location, size

    x, y, width, height = location.get("x"), location.get("y"), size.get("width"), size.get("height")
    assert x and y and width and height

    x, y = x + width // 2, y + height // 2
    return x, y

with webdriver.Chrome(...) as driver:
    sync_input = SyncInput(browser=driver)

    # Example: Click Button
    # Find Button Coords
    locator = driver.find_element(By.XPATH, "//button")
    x, y = get_locator_pos(locator)
    # Click Coords => Click Button
    sync_input.click("left", x, y)
```

***

## Async Usage (Async Selenium-Driverless)

```python
from selenium_driverless import webdriver
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

async with async_webdriver.Chrome(options) as driver:
    async_input = await AsyncInput(browser=driver)

    # Example: Click Button
    # Find Button Coords
    locator = await async_driver.find_element(By.XPATH, "//button")
    x, y = await get_locator_pos(locator)
    # Click Coords => Click Button
    await aawait async_driver.find_element(By.XPATH, "//button")sync_input.click("left", x, y)
```
