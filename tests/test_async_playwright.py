import asyncio

import pytest
from playwright.async_api import Locator, Page

from cdp_patches.input.exceptions import WindowClosedException
from tests.server import Server

# from input import KeyboardCodes


async def get_locator_pos(locator: Locator):
    bounding_box = await locator.bounding_box()
    assert bounding_box

    x, y, width, height = bounding_box.get("x"), bounding_box.get("y"), bounding_box.get("width"), bounding_box.get("height")
    assert x and y and width and height

    x, y = x + width // 2, y + height // 2
    return x, y


@pytest.mark.asyncio
async def test_input_leak(async_page: Page, server: Server) -> None:
    await async_page.goto(server.PREFIX + "/input/button.html")
    await async_page.evaluate(
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
    async_locator = async_page.locator("button")
    x, y = await get_locator_pos(async_locator)
    await async_page.async_input.click("left", x, y)  # type: ignore[attr-defined]

    is_leaking = await async_page.evaluate("() => window.is_leaking")
    assert not is_leaking


@pytest.mark.asyncio
async def test_click_the_button(async_page: Page, server: Server) -> None:
    await async_page.goto(server.PREFIX + "/input/button.html")
    locator = async_page.locator("button")
    x, y = await get_locator_pos(locator)
    await async_page.async_input.click("left", x, y)  # type: ignore[attr-defined]
    assert await async_page.evaluate("result") == "Clicked"


@pytest.mark.asyncio
async def test_double_click_the_button(async_page: Page, server: Server) -> None:
    await async_page.goto(server.PREFIX + "/input/button.html")
    await async_page.evaluate(
        """() => {
            window.double = false;
            button = document.querySelector('button');
            button.addEventListener('dblclick', event => window.double = true);
        }"""
    )

    locator = async_page.locator("button")
    x, y = await get_locator_pos(locator)
    await async_page.async_input.double_click("left", x, y)  # type: ignore[attr-defined]
    await asyncio.sleep(0.1)
    assert await async_page.evaluate("double")
    assert await async_page.evaluate("result") == "Clicked"


@pytest.mark.asyncio
async def test_locators_hover(async_page: Page, server: Server) -> None:
    await async_page.goto(server.PREFIX + "/input/scrollable.html")
    await async_page.async_input.move(500, 100)  # type: ignore[attr-defined]

    button = async_page.locator("#button-12")
    x, y = await get_locator_pos(button)
    await async_page.async_input.move(x, y)  # type: ignore[attr-defined]

    await asyncio.sleep(0.5)
    assert await async_page.evaluate("window.last_hover_elem.id") == "button-12"


@pytest.mark.skip(reason="Scroll Tests currently arent implemented properly.")
@pytest.mark.asyncio
async def test_scroll(async_page: Page, server: Server) -> None:
    await async_page.goto(server.PREFIX + "/offscreenbuttons.html")
    for i in range(11):
        button = await async_page.query_selector(f"#btn{i}")
        assert button
        before = await button.evaluate(
            """button => {
                return button.getBoundingClientRect().right - window.innerWidth
            }"""
        )

        assert before == 10 * i
        # await button.scroll_into_view_if_needed()
        await async_page.async_input.scroll("right", i)  # type: ignore[attr-defined]

        after = await button.evaluate(
            """button => {
                return button.getBoundingClientRect().right - window.innerWidth
            }"""
        )

        assert after <= 0
        await async_page.evaluate("() => window.scrollTo(0, 0)")


@pytest.mark.asyncio
async def test_fill_input(async_page: Page, server: Server) -> None:
    await async_page.goto(server.PREFIX + "/input/textarea.html")
    handle = async_page.locator("input")
    assert handle

    x, y = await get_locator_pos(handle)
    await async_page.async_input.click("left", x, y)  # type: ignore[attr-defined]
    await async_page.async_input.type("some value", fill=True)  # type: ignore[attr-defined]
    assert await async_page.evaluate("result") == "some value"


@pytest.mark.asyncio
async def test_keyboard_type_into_a_textarea(async_page: Page) -> None:
    await async_page.evaluate(
        """
            const textarea = document.createElement('textarea');
            document.body.appendChild(textarea);
            textarea.focus();
        """
    )
    text = "Hello world. I +am  the %text that was typed!"

    handle = async_page.locator("textarea")
    assert handle

    x, y = await get_locator_pos(handle)
    await async_page.async_input.click("left", x, y)  # type: ignore[attr-defined]

    await async_page.async_input.type(text)  # type: ignore[attr-defined]
    assert await async_page.evaluate('document.querySelector("textarea").value') == text


# @pytest.mark.asyncio
# async def test_should_report_shiftkey(async_page: Page, server: Server) -> None:
#     await async_page.goto(server.PREFIX + "/input/keyboard.html")
#     code_for_key = {KeyboardCodes.VK_SHIFT: ["Shift", "16"], KeyboardCodes.VK_CONTROL: ["Control", "17"]}
#     # , KeyboardCodes.VK_MENU: ["Alt", "18"]
#
#     handle = async_page.locator("textarea")
#     assert handle
#
#     x, y = await get_locator_pos(handle)
#     await async_page.async_input.click("left", x, y)   # type: ignore[attr-defined]
#
#     for modifier_key, js_key in code_for_key.items():
#         await async_page.async_input.press_keys(modifier_key)   # type: ignore[attr-defined]
#         # async_page.async_input._base.browser_window.send_keystrokes("{VK_SHIFT down} bruh")   # type: ignore[attr-defined]
#
#         assert (
#             await async_page.evaluate("() => getResult()")
#             == "Keydown: "
#             + js_key[0]
#             + " "
#             + js_key[0]
#             + "Left "
#             + js_key[1]
#             + " ["
#             + js_key[0]
#             + "]"
#         )
#
#         await async_page.async_input.press_keys("!")   # type: ignore[attr-defined]
#         # Shift+! will generate a keypress
#         if js_key[0] == "Shift":
#             assert (
#                 await async_page.evaluate("() => getResult()")
#                 == "Keydown: ! Digit1 49 ["
#                 + js_key[0]
#                 + "]\nKeypress: ! Digit1 33 33 ["
#                 + js_key[0]
#                 + "]"
#             )
#         else:
#             assert (
#                 await async_page.evaluate("() => getResult()")
#                 == "Keydown: ! Digit1 49 [" + js_key[0] + "]"
#             )
#
#         await async_page.async_input.release_keys("!")   # type: ignore[attr-defined]
#         assert (
#             await async_page.evaluate("() => getResult()")
#             == "Keyup: ! Digit1 49 [" + js_key[0] + "]"
#         )
#         await async_page.async_input.release_keys(modifier_key)   # type: ignore[attr-defined]
#         assert (
#             await async_page.evaluate("() => getResult()")
#             == "Keyup: "
#             + js_key[0]
#             + " "
#             + js_key[0]
#             + "Left "
#             + js_key[1]
#             + " []"
#         )


@pytest.mark.asyncio
async def test_quit_exception(async_page: Page) -> None:
    await async_page.close()
    await asyncio.sleep(5)

    with pytest.raises(WindowClosedException):
        await async_page.async_input.down("left", 100, 100, emulate_behaviour=False)  # type: ignore[attr-defined]
    with pytest.raises(WindowClosedException):
        await async_page.async_input.up("left", 110, 110)  # type: ignore[attr-defined]
    with pytest.raises(WindowClosedException):
        await async_page.async_input.move(50, 50, emulate_behaviour=False)  # type: ignore[attr-defined]
    with pytest.raises(WindowClosedException):
        await async_page.async_input.scroll("up", 10)  # type: ignore[attr-defined]
    with pytest.raises(WindowClosedException):
        await async_page.async_input.type("test")  # type: ignore[attr-defined]
