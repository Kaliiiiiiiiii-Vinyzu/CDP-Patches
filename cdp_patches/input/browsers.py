from typing import Dict, List, TypedDict, Union

from playwright.async_api import Browser as AsyncBrowser
from playwright.async_api import BrowserContext as AsyncContext
from playwright.sync_api import Browser as SyncBrowser
from playwright.sync_api import BrowserContext as SyncContext
from selenium import webdriver
from selenium_driverless import webdriver as driverless_async_webdriver
from selenium_driverless.sync import webdriver as driverless_sync_webdriver

all_browsers = Union[webdriver.Chrome, SyncContext, SyncBrowser, AsyncContext, AsyncBrowser, driverless_sync_webdriver.Chrome, driverless_async_webdriver.Chrome]
sync_browsers = Union[webdriver.Chrome, SyncContext, SyncBrowser, driverless_sync_webdriver.Chrome]
async_browsers = Union[AsyncContext, AsyncBrowser, driverless_async_webdriver.Chrome]


class InternalProcessInfo(TypedDict):
    type: str
    id: int
    cpuTime: float


class CDPProcessInfo:
    processInfo: List[InternalProcessInfo]

    def __init__(self, process_info: Dict[str, List[InternalProcessInfo]]) -> None:
        self.processInfo = process_info["processInfo"]

    def get_main_browser(self) -> InternalProcessInfo:
        for process in self.processInfo:
            if process.get("type") == "browser":
                return process

        raise ValueError("No browser process found.")


# Browser PID
# Selenium & Selenium Driverless
def get_sync_selenium_browser_pid(driver: Union[webdriver.Chrome, driverless_sync_webdriver.Chrome]) -> int:
    if isinstance(driver, driverless_sync_webdriver.Chrome):
        cdp_system_info = driver.base_target.execute_cdp_cmd(cmd="SystemInfo.getProcessInfo")
    else:
        cdp_system_info = driver.execute_cdp_cmd(cmd="SystemInfo.getProcessInfo", cmd_args={})

    process_info = CDPProcessInfo(cdp_system_info)
    browser_info = process_info.get_main_browser()
    return browser_info["id"]


async def get_async_selenium_browser_pid(driver: driverless_async_webdriver.Chrome) -> int:
    cdp_system_info = await driver.base_target.execute_cdp_cmd(cmd="SystemInfo.getProcessInfo")

    process_info = CDPProcessInfo(cdp_system_info)
    browser_info = process_info.get_main_browser()
    return browser_info["id"]


# Playwright
def get_sync_playwright_browser_pid(browser: Union[SyncContext, SyncBrowser]) -> int:
    if isinstance(browser, SyncContext):
        main_browser = browser.browser
        assert main_browser
        cdp_session = main_browser.new_browser_cdp_session()
    elif isinstance(browser, SyncBrowser):
        cdp_session = browser.new_browser_cdp_session()
    else:
        raise ValueError("Invalid browser type.")

    cdp_system_info = cdp_session.send("SystemInfo.getProcessInfo")

    process_info = CDPProcessInfo(cdp_system_info)
    browser_info = process_info.get_main_browser()
    return browser_info["id"]


async def get_async_playwright_browser_pid(browser: Union[AsyncContext, AsyncBrowser]) -> int:
    if isinstance(browser, AsyncContext):
        main_browser = browser.browser
        assert main_browser
        cdp_session = await main_browser.new_browser_cdp_session()
    elif isinstance(browser, AsyncBrowser):
        cdp_session = await browser.new_browser_cdp_session()
    else:
        raise ValueError("Invalid browser type.")
    cdp_system_info = await cdp_session.send("SystemInfo.getProcessInfo")

    process_info = CDPProcessInfo(cdp_system_info)
    browser_info = process_info.get_main_browser()
    return browser_info["id"]


def get_sync_browser_pid(browser: sync_browsers) -> int:
    if isinstance(browser, webdriver.Chrome) or isinstance(browser, driverless_sync_webdriver.Chrome):
        return get_sync_selenium_browser_pid(browser)
    elif isinstance(browser, SyncContext) or isinstance(browser, SyncBrowser):
        return get_sync_playwright_browser_pid(browser)

    raise ValueError("Invalid browser type.")


async def get_async_browser_pid(browser: async_browsers) -> int:
    if isinstance(browser, driverless_async_webdriver.Chrome):
        return await get_async_selenium_browser_pid(browser)
    elif isinstance(browser, AsyncContext) or isinstance(browser, AsyncBrowser):
        return await get_async_playwright_browser_pid(browser)

    raise ValueError("Invalid browser type.")


# Scale Factor
# Selenium & Selenium Driverless
def get_sync_selenium_scale_factor(driver: Union[webdriver.Chrome, driverless_sync_webdriver.Chrome]) -> int:
    scale_factor: int = driver.execute_script("return window.devicePixelRatio")
    return scale_factor


async def get_async_selenium_scale_factor(driver: driverless_async_webdriver.Chrome) -> int:
    scale_factor: int = await driver.execute_script("return window.devicePixelRatio")
    return scale_factor


# Playwright
def get_sync_playwright_scale_factor(browser: Union[SyncContext, SyncBrowser]) -> int:
    if isinstance(browser, SyncContext) and any(browser.pages):
        page = browser.pages[0]
    else:
        page = browser.new_page()

    scale_factor: int = page.evaluate("window.devicePixelRatio")
    if not (isinstance(browser, SyncContext) and any(browser.pages)):
        page.close()

    return scale_factor


async def get_async_playwright_scale_factor(browser: Union[AsyncContext, AsyncBrowser]) -> int:
    if isinstance(browser, AsyncContext) and any(browser.pages):
        page = browser.pages[0]
    else:
        page = await browser.new_page()

    scale_factor: int = await page.evaluate("window.devicePixelRatio")
    if not (isinstance(browser, AsyncContext) and any(browser.pages)):
        await page.close()

    return scale_factor


def get_sync_scale_factor(browser: sync_browsers) -> int:
    if isinstance(browser, webdriver.Chrome) or isinstance(browser, driverless_sync_webdriver.Chrome):
        return get_sync_selenium_scale_factor(browser)
    elif isinstance(browser, SyncContext) or isinstance(browser, SyncBrowser):
        return get_sync_playwright_scale_factor(browser)

    raise ValueError("Invalid browser type.")


async def get_async_scale_factor(browser: async_browsers) -> int:
    if isinstance(browser, driverless_async_webdriver.Chrome):
        return await get_async_selenium_scale_factor(browser)
    elif isinstance(browser, AsyncContext) or isinstance(browser, AsyncBrowser):
        return await get_async_playwright_scale_factor(browser)

    raise ValueError("Invalid browser type.")
