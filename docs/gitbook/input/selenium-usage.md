# Selenium Usage



## Sync Usage (Selenium)

```python
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
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

options = webdriver.ChromeOptions()
# disable logs & automation
options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_argument("--log-level=3")

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
import asyncio
from selenium_driverless import webdriver
from selenium_driverless.types.by import By
from cdp_patches.input import AsyncInput

async def main():
    async with webdriver.Chrome(...) as driver:
        async_input = await AsyncInput(browser=driver)
    
        # Example: Click Button
        # Find Button Coords
        locator = await driver.find_element(By.XPATH, "//button")
        x, y = await locator.mid_location()
        # Click Coords => Click Button
        await async_input.click("left", x, y)

asyncio.run(main())
```
