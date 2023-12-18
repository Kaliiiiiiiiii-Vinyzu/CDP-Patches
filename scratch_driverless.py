from selenium_driverless import webdriver
import asyncio
from pyinput.asyncio import BasePointer
from pyinput.utils import find_chrome_window, get_active_document


async def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--auto-open-devtools-for-tabs")
    options.add_argument('--force-renderer-accessibility')
    options.prefs.update({'devtools':{
                        'preferences':{
                            # always open devtools in undocked
                            'currentDockState': '"undocked"',
                            # always open devtools with console open
                            'panel-selectedTab': '"console"'}
                            }
                       })
    async with webdriver.Chrome(options=options) as driver:
        debug_script = """
        document.addEventListener("click", console.log);
        document.addEventListener("mousedown", console.log);
        document.addEventListener("mouseup", console.log);
        document.addEventListener("keydown", console.log);
        document.addEventListener("keyup", console.log);
        """
        await driver.execute_script(debug_script)
        scale_factor = await driver.execute_script("return window.devicePixelRatio")
        # await driver.maximize_window()

        windows = find_chrome_window(driver.browser_pid)
        hwnd = get_active_document(windows[0]).handle
        pointer = BasePointer(hwnd, scale_factor)

        await pointer.click(100, 100)
        pointer.down(1, 1)
        pointer.down(20, 20)
        pointer.down(300, 300)
        pointer.down(40, 40)

        print(await driver.title)


asyncio.run(main())
