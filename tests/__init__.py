from selenium_driverless import webdriver
from selenium_driverless.types.by import By
from cdp_patches.input import AsyncInput
import asyncio


async def main():
    options = webdriver.ChromeOptions()
    async with webdriver.Chrome(options=options) as driver:
        async_input = await AsyncInput(browser=driver)
        await driver.get('https://kaliiiiiiiiii.github.io/brotector/', wait_load=True)
        locator = await driver.find_element(By.XPATH, '/html/body/div/h1')
        x, y = await locator.mid_location()
        # Click Coords => Click Button
        await async_input.click("left", x, y)
        await driver.sleep(1000000)


asyncio.run(main())
