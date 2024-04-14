from tests.server import Server
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


def get_locator_pos(locator: WebElement):
    location = locator.location
    size = locator.size
    assert location, size

    x, y, width, height = location.get("x"), location.get("y"), size.get("width"), size.get("height")
    assert x and y and width and height

    x, y = x + width // 2, y + height // 2
    return x, y


def test_input_leak(selenium_driver: Chrome, server: Server) -> None:
    selenium_driver.get(server.PREFIX + "/input/button.html")
    selenium_driver.execute_script(
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
    sync_locator = selenium_driver.find_element(By.XPATH, "//button")
    x, y = get_locator_pos(sync_locator)
    selenium_driver.sync_input.click("left", x, y)  # type: ignore[attr-defined]

    is_leaking = selenium_driver.execute_async_script("window.is_leaking.then(arguments[arguments.length - 1])")
    assert not is_leaking
