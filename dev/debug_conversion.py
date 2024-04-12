import asyncio
import os
import typing

from selenium_driverless.webdriver import Chrome, ChromeOptions
from selenium_driverless.utils.utils import find_chrome_executable
from playwright.async_api import async_playwright
from cdp_patches.input import AsyncInput
from tests.conftest import flags
import subprocess

import ctypes


async def get_conversion(async_driver: typing.Union[Chrome, async_playwright] = None) -> typing.Tuple[
        typing.List[typing.Tuple], typing.List[typing.Tuple]]:
    points = [
        (100, 100),
        (110, 120),
        (120, 110),
        (110, 120),
        (100, 110),
        (110, 100),
        (100, 120),
        (120, 100),
        (120, 120)
    ]
    script = """
            window.cords = []
            document.body.addEventListener("click", (event)=>{
                window.cords.push([event.x, event.y])
            })
            """
    if isinstance(async_driver, Chrome):
        await async_driver.execute_script(script)
    else:
        await async_driver.evaluate(f'() => {{{script}}}')

    await asyncio.sleep(0.1)
    for x, y in points:
        await async_driver.async_input.click("left", x, y)  # type: ignore[attr-defined]
        await asyncio.sleep(0.1)

    if isinstance(async_driver, Chrome):
        points_received = await async_driver.execute_script("return window.cords")
    else:
        points_received = await async_driver.evaluate('() => {return window.cords}')
    return points, list([(x, y) for x, y in points_received])


def is_aware(pid: int) -> bool:
    process_handle = None
    try:
        process_handle = ctypes.windll.kernel32.OpenProcess(
            0,  # no permissions
            False,  # bInheritHandle
            pid
        )
        aware = ctypes.c_int()
        ctypes.windll.shcore.GetProcessDpiAwareness(
            process_handle,
            ctypes.byref(aware)
        )
    finally:
        if process_handle:
            ctypes.windll.kernel32.CloseHandle(process_handle)
    return aware


async def conversion_driverless() -> typing.Tuple[typing.List[typing.Tuple], typing.List[typing.Tuple]]:
    options = ChromeOptions()
    for flag in flags:
        options.add_argument(flag)
    options.add_argument("--device-scale-factor=0.4")
    async with Chrome() as driver:
        async_input = await AsyncInput(browser=driver)

        is_dpi_aware = is_aware(async_input.pid)
        if is_dpi_aware:
            async_input.scale_factor = async_input.scale_factor * (
                    ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100)

        driver.async_input = async_input
        return await get_conversion(driver)


async def conversion_playwright() -> typing.Tuple[typing.List[typing.Tuple], typing.List[typing.Tuple]]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=flags)
        context = await browser.new_context(locale="en-US")
        page = await context.new_page()
        async_input = await AsyncInput(browser=context)

        is_dpi_aware = is_aware(async_input.pid)
        if is_dpi_aware:
            async_input.scale_factor = async_input.scale_factor * (
                        ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100)

        page.async_input = async_input
        return await get_conversion(page)


async def main():
    driverless, playwright = await asyncio.gather(
        conversion_driverless(),
        conversion_playwright()
    )
    print("Driverless:")
    print(driverless[0])
    print(driverless[1])
    print("\n")
    print("Playwright:")
    print(playwright[0])
    print(playwright[1])


async def run_default() -> typing.List[typing.Tuple]:
    proc = None
    try:
        proc = subprocess.Popen(find_chrome_executable())
        breakpoint()
        points = [
            (100, 100),
            (110, 120),
            (120, 110),
            (110, 120),
            (100, 110),
            (110, 100),
            (100, 120),
            (120, 100),
            (120, 120)
        ]
        async_input = await AsyncInput(proc.pid)

        await asyncio.sleep(0.1)
        for x, y in points:
            await async_input.click("left", x, y)  # type: ignore[attr-defined]
            await asyncio.sleep(0.1)
        print(points)
        return points
    finally:
        if proc:
            breakpoint()
            os.kill(proc.pid, 7)


if __name__ == "__main__":
    asyncio.run(main())
    # asyncio.run(run_default())
