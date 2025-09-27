import json
import time
from contextlib import suppress
from typing import Dict, List, Type, TypedDict, Union

import requests
from websockets.sync import client

try:
    from playwright.async_api import Browser as AsyncBrowser
    from playwright.async_api import BrowserContext as AsyncContext
    from playwright.async_api import Error as AsyncError
    from playwright.async_api import Error as SyncError
    from playwright.sync_api import Browser as SyncBrowser
    from playwright.sync_api import BrowserContext as SyncContext
except ImportError:
    AsyncBrowser: Type["AsyncBrowser"] = "AsyncBrowser"  # type: ignore[no-redef]
    AsyncContext: Type["AsyncContext"] = "AsyncContext"  # type: ignore[no-redef]
    SyncBrowser: Type["SyncBrowser"] = "SyncBrowser"  # type: ignore[no-redef]
    SyncContext: Type["SyncContext"] = "SyncContext"  # type: ignore[no-redef]

try:
    from botright.extended_typing import BrowserContext as BotrightContext
except ImportError:
    BotrightContext: Type["BotrightContext"] = "BotrightContext"  # type: ignore[no-redef]

try:
    from selenium.webdriver import Chrome as SeleniumChrome
except ImportError:
    SeleniumChrome: Type["SeleniumChrome"] = type("SeleniumChrome", (object,), {})  # type: ignore[no-redef]

try:
    from selenium_driverless.sync.webdriver import Chrome as DriverlessSyncChrome
    from selenium_driverless.webdriver import Chrome as DriverlessAsyncChrome
except ImportError:
    DriverlessAsyncChrome: Type["DriverlessAsyncChrome"] = type("DriverlessAsyncChrome", (object,), {})  # type: ignore[no-redef]
    DriverlessSyncChrome: Type["DriverlessSyncChrome"] = type("DriverlessSyncChrome", (object,), {})  # type: ignore[no-redef]

all_browsers = Union[AsyncContext, AsyncBrowser, SyncContext, SyncBrowser, BotrightContext, SeleniumChrome, DriverlessAsyncChrome, DriverlessSyncChrome]
sync_browsers = Union[SeleniumChrome, SyncContext, SyncBrowser, DriverlessSyncChrome]
async_browsers = Union[AsyncContext, AsyncBrowser, BotrightContext, DriverlessAsyncChrome]


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


class SeleniumProcessInfoResponse(TypedDict):
    id: int
    result: Dict[str, List[InternalProcessInfo]]


def process_info_from_ws(ws_url: str) -> Dict[str, List[InternalProcessInfo]]:
    with client.connect(ws_url) as websocket:
        websocket.send(json.dumps({"id": 1, "method": "SystemInfo.getProcessInfo"}))
        for message in websocket:
            data: SeleniumProcessInfoResponse = json.loads(message)
            if data.get("id") == 1:
                return data["result"]

    raise RuntimeError("Couldn't connect to browser.")


def ws_url_from_url(url: str, timeout: float = 30) -> str:
    if len(url) < 7 or url[:7] != "http://":
        url = "http://" + url + "/json/version"
    try:
        data = requests.get(url, timeout=timeout).json()
    except requests.exceptions.Timeout:
        raise TimeoutError(f"Couldn't connect to browser within {timeout} seconds")

    websocket_debugger_url: str = data["webSocketDebuggerUrl"]
    return websocket_debugger_url


def process_info_from_url(url: str) -> Dict[str, List[InternalProcessInfo]]:
    ws_url = ws_url_from_url(url)
    return process_info_from_ws(ws_url)


# Browser PID
# Selenium & Selenium Driverless
def get_sync_selenium_browser_pid(driver: Union[SeleniumChrome, DriverlessSyncChrome]) -> int:
    if isinstance(driver, DriverlessSyncChrome):
        cdp_system_info = driver.base_target.execute_cdp_cmd(cmd="SystemInfo.getProcessInfo")
    elif isinstance(driver, SeleniumChrome):
        cdp_system_info = process_info_from_url(driver.capabilities["goog:chromeOptions"]["debuggerAddress"])
    else:
        raise ValueError("Invalid browser type.")
    process_info = CDPProcessInfo(cdp_system_info)
    browser_info = process_info.get_main_browser()
    return browser_info["id"]


async def get_async_selenium_browser_pid(driver: DriverlessAsyncChrome) -> int:
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


async def get_async_playwright_browser_pid(browser: Union[AsyncContext, AsyncBrowser, BotrightContext]) -> int:
    if isinstance(browser, AsyncContext) or isinstance(browser, BotrightContext):
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
    if isinstance(browser, SeleniumChrome) or isinstance(browser, DriverlessSyncChrome):
        return get_sync_selenium_browser_pid(browser)
    elif isinstance(browser, SyncContext) or isinstance(browser, SyncBrowser):
        return get_sync_playwright_browser_pid(browser)

    raise ValueError("Invalid browser type.")


async def get_async_browser_pid(browser: async_browsers) -> int:
    if isinstance(browser, DriverlessAsyncChrome):
        return await get_async_selenium_browser_pid(browser)
    elif isinstance(browser, AsyncContext) or isinstance(browser, AsyncBrowser) or isinstance(browser, BotrightContext):
        return await get_async_playwright_browser_pid(browser)

    raise ValueError("Invalid browser type.")


# Scale Factor
# Selenium & Selenium Driverless
def get_sync_selenium_scale_factor(driver: Union[SeleniumChrome, DriverlessSyncChrome]) -> int:
    if isinstance(driver, DriverlessSyncChrome):
        _scale_factor: int = driver.execute_script("return window.devicePixelRatio", unique_context=True)
        return _scale_factor

    scale_factor: int = driver.execute_script("return window.devicePixelRatio")
    return scale_factor


async def get_async_selenium_scale_factor(driver: DriverlessAsyncChrome) -> int:
    scale_factor: int = await driver.execute_script("return window.devicePixelRatio", unique_context=True)
    return scale_factor


# Playwright with Runtime Patching
def get_sync_playwright_scale_factor(browser: Union[SyncContext, SyncBrowser]) -> int:
    close_context, close_page = False, False
    if isinstance(browser, SyncContext):
        context = browser
    elif isinstance(browser, SyncBrowser):
        if any(browser.contexts):
            context = browser.contexts[0]
        else:
            context = browser.new_context()
            close_context = True
    else:
        raise ValueError("Invalid browser type.")

    if any(context.pages):
        page = context.pages[0]
    else:
        page = context.new_page()
        close_page = True
    cdp_session = context.new_cdp_session(page)

    time1 = time.perf_counter()
    while (time.perf_counter() - time1) <= 10:
        try:
            page_frame_tree = cdp_session.send("Page.getFrameTree")
            page_id = page_frame_tree["frameTree"]["frame"]["id"]

            isolated_world = cdp_session.send("Page.createIsolatedWorld", {"frameId": page_id, "grantUniveralAccess": True, "worldName": "Shimmy shimmy yay, shimmy yay, shimmy ya"})
            isolated_exec_id = isolated_world["executionContextId"]
            break
        except SyncError as e:
            if e.message == "Protocol error (Page.createIsolatedWorld): Invalid parameters":
                pass
            else:
                raise e
    else:
        raise TimeoutError("Page.createIsolatedWorld did not initialize properly within 30 seconds.")

    time2 = time.perf_counter()
    while (time.perf_counter() - time2) <= 10:
        try:
            scale_factor_eval = cdp_session.send("Runtime.evaluate", {"expression": "window.devicePixelRatio", "contextId": isolated_exec_id})
            scale_factor: int = scale_factor_eval["result"]["value"]
            break
        except SyncError as e:
            if e.message == "Protocol error (Runtime.evaluate): Cannot find context with specified id":
                pass
            else:
                raise e
    else:
        raise TimeoutError("Runtime.evaluate did not run properly within 30 seconds.")

    with suppress(SyncError):
        if close_page:
            page.close()

    with suppress(SyncError):
        if close_context:
            context.close()

    return scale_factor


async def get_async_playwright_scale_factor(browser: Union[AsyncContext, AsyncBrowser, BotrightContext]) -> int:
    close_context, close_page = False, False
    if isinstance(browser, AsyncContext) or isinstance(browser, BotrightContext):
        context = browser
    elif isinstance(browser, AsyncBrowser):
        if any(browser.contexts):
            context = browser.contexts[0]
        else:
            context = await browser.new_context()
            close_context = True
    else:
        raise ValueError("Invalid browser type.")

    if any(context.pages):
        page = context.pages[0]
    else:
        page = await context.new_page()
        close_page = True
    cdp_session = await context.new_cdp_session(page)

    time1 = time.perf_counter()
    while (time.perf_counter() - time1) <= 10:
        try:
            page_frame_tree = await cdp_session.send("Page.getFrameTree")
            page_id = page_frame_tree["frameTree"]["frame"]["id"]

            isolated_world = await cdp_session.send("Page.createIsolatedWorld", {"frameId": page_id, "grantUniveralAccess": True, "worldName": "Shimmy shimmy yay, shimmy yay, shimmy ya"})
            isolated_exec_id = isolated_world["executionContextId"]
            break
        except AsyncError as e:
            if e.message == "Protocol error (Page.createIsolatedWorld): Invalid parameters":
                pass
            else:
                raise e
    else:
        raise TimeoutError("Page.createIsolatedWorld did not initialize properly within 30 seconds.")

    time2 = time.perf_counter()
    while (time.perf_counter() - time2) <= 10:
        try:
            scale_factor_eval = await cdp_session.send("Runtime.evaluate", {"expression": "window.devicePixelRatio", "contextId": isolated_exec_id})
            scale_factor: int = scale_factor_eval["result"]["value"]
            break
        except AsyncError as e:
            if e.message == "Protocol error (Runtime.evaluate): Cannot find context with specified id":
                pass
            else:
                raise e
    else:
        raise TimeoutError("Runtime.evaluate did not run properly within 30 seconds.")

    with suppress(SyncError):
        if close_page:
            await page.close()

    with suppress(SyncError):
        if close_context:
            await context.close()

    return scale_factor


def get_sync_scale_factor(browser: sync_browsers) -> int:
    if isinstance(browser, SeleniumChrome) or isinstance(browser, DriverlessSyncChrome):
        return get_sync_selenium_scale_factor(browser)
    elif isinstance(browser, SyncContext) or isinstance(browser, SyncBrowser):
        return get_sync_playwright_scale_factor(browser)

    raise ValueError("Invalid browser type.")


async def get_async_scale_factor(browser: async_browsers) -> int:
    if isinstance(browser, DriverlessAsyncChrome):
        return await get_async_selenium_scale_factor(browser)
    elif isinstance(browser, AsyncContext) or isinstance(browser, AsyncBrowser) or isinstance(browser, BotrightContext):
        return await get_async_playwright_scale_factor(browser)

    raise ValueError("Invalid browser type.")


__all__ = ["SeleniumChrome", "DriverlessSyncChrome", "DriverlessAsyncChrome"]
