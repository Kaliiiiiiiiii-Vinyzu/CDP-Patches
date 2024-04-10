import asyncio

from selenium_driverless.webdriver import Chrome, ChromeOptions
from selenium_driverless.types.webelement import WebElement
from selenium_driverless.types.by import By
from tests.server import Server, test_server
from cdp_patches.input import AsyncInput
from tests.conftest import flags


async def get_locator_pos(locator: WebElement):
    location = await locator.location
    size = await locator.size
    assert location, size

    x, y, width, height = location.get("x"), location.get("y"), size.get("width"), size.get("height")
    assert x and y and width and height

    x, y = x + width // 2, y + height // 2
    return x, y


async def input_leak_test(async_driver: Chrome, server: Server) -> None:
    await async_driver.get(server.PREFIX + "/input/button.html")
    await async_driver.execute_script(
        """
        const click_elem = document.querySelector("button")
        window.is_leaking = new Promise((resolve, reject) => {callback = resolve});
        const on_click = async function(e){
                var is_bot = (e.pageY == e.screenY && e.pageX == e.screenX)
                if (is_bot && 1 >= outerHeight - innerHeight){ // fullscreen
                    is_bot = false
                }
                callback(is_bot)
        }
        click_elem.removeEventListener("mousedown", self)
        click_elem.addEventListener("mousedown", on_click)
    """
    )
    sync_locator = await async_driver.find_element(By.XPATH, "//button")
    x, y = await get_locator_pos(sync_locator)
    await async_driver.async_input.click("left", x, y)  # type: ignore[attr-defined]

    is_leaking = await async_driver.eval_async("return await window.is_leaking", timeout=300)
    print("Passed!")
    assert not is_leaking


async def main():
    test_server.start()
    try:
        options = ChromeOptions()
        for flag in flags:
            options.add_argument(flag)
        async with Chrome() as driver:
            driver.async_input = await AsyncInput(browser=driver)
            await input_leak_test(driver, test_server.server)
    finally:
        test_server.stop()


asyncio.run(main())
