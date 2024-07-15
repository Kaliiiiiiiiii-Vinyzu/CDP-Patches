import time

import pytest
from playwright.sync_api import Locator, Page

from cdp_patches.input.exceptions import WindowClosedException
from tests.server import Server

# from input import KeyboardCodes


def get_locator_pos(locator: Locator):
    bounding_box = locator.bounding_box()
    assert bounding_box

    x, y, width, height = bounding_box.get("x"), bounding_box.get("y"), bounding_box.get("width"), bounding_box.get("height")
    assert x and y and width and height

    x, y = x + width // 2, y + height // 2
    return x, y


def test_input_leak(sync_page: Page, server: Server) -> None:
    sync_page.goto(server.PREFIX + "/input/button.html")
    sync_page.evaluate(
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
    sync_locator = sync_page.locator("button")
    x, y = get_locator_pos(sync_locator)
    sync_page.sync_input.click("left", x, y)  # type: ignore[attr-defined]

    is_leaking = sync_page.evaluate("() => window.is_leaking")
    assert not is_leaking


def test_click_the_button(sync_page: Page, server: Server) -> None:
    sync_page.goto(server.PREFIX + "/input/button.html")
    locator = sync_page.locator("button")
    x, y = get_locator_pos(locator)
    sync_page.sync_input.click("left", x, y)  # type: ignore[attr-defined]
    assert sync_page.evaluate("result") == "Clicked"


def test_double_click_the_button(sync_page: Page, server: Server) -> None:
    sync_page.goto(server.PREFIX + "/input/button.html")
    sync_page.evaluate(
        """() => {
            window.double = false;
            button = document.querySelector('button');
            button.addEventListener('dblclick', event => window.double = true);
        }"""
    )

    locator = sync_page.locator("button")
    x, y = get_locator_pos(locator)
    sync_page.sync_input.double_click("left", x, y)  # type: ignore[attr-defined]
    time.sleep(0.1)
    assert sync_page.evaluate("double")
    assert sync_page.evaluate("result") == "Clicked"


def test_locators_hover(sync_page: Page, server: Server) -> None:
    sync_page.goto(server.PREFIX + "/input/scrollable.html")
    sync_page.sync_input.move(500, 100)  # type: ignore[attr-defined]

    button = sync_page.locator("#button-12")
    x, y = get_locator_pos(button)
    sync_page.sync_input.move(x, y)  # type: ignore[attr-defined]

    time.sleep(0.5)
    assert sync_page.evaluate("window.last_hover_elem.id") == "button-12"


@pytest.mark.skip(reason="Scroll Tests currently arent implemented properly.")
def test_scroll(sync_page: Page, server: Server) -> None:
    sync_page.goto(server.PREFIX + "/offscreenbuttons.html")
    for i in range(11):
        button = sync_page.query_selector(f"#btn{i}")
        assert button
        before = button.evaluate(
            """button => {
                return button.getBoundingClientRect().right - window.innerWidth
            }"""
        )

        assert before == 10 * i
        # button.scroll_into_view_if_needed()
        sync_page.sync_input.scroll("right", i)  # type: ignore[attr-defined]

        after = button.evaluate(
            """button => {
                return button.getBoundingClientRect().right - window.innerWidth
            }"""
        )

        assert after <= 0
        sync_page.evaluate("() => window.scrollTo(0, 0)")


def test_fill_input(sync_page: Page, server: Server) -> None:
    sync_page.goto(server.PREFIX + "/input/textarea.html")
    handle = sync_page.locator("input")
    assert handle

    x, y = get_locator_pos(handle)
    sync_page.sync_input.click("left", x, y)  # type: ignore[attr-defined]
    sync_page.sync_input.type("some value", fill=True)  # type: ignore[attr-defined]
    assert sync_page.evaluate("result") == "some value"


def test_keyboard_type_into_a_textarea(sync_page: Page) -> None:
    sync_page.evaluate(
        """
            const textarea = document.createElement('textarea');
            document.body.appendChild(textarea);
            textarea.focus();
        """
    )
    text = "Hello world. I +am  the %text that was typed!"

    handle = sync_page.locator("textarea")
    assert handle

    x, y = get_locator_pos(handle)
    sync_page.sync_input.click("left", x, y)  # type: ignore[attr-defined]

    sync_page.sync_input.type(text)  # type: ignore[attr-defined]
    assert sync_page.evaluate('document.querySelector("textarea").value') == text


# def test_should_report_shiftkey(sync_page: Page, server: Server) -> None:
#     sync_page.goto(server.PREFIX + "/input/keyboard.html")
#     code_for_key = {KeyboardCodes.VK_SHIFT: ["Shift", "16"], KeyboardCodes.VK_CONTROL: ["Control", "17"]}
#     # , KeyboardCodes.VK_MENU: ["Alt", "18"]
#
#     handle = sync_page.locator("textarea")
#     assert handle
#
#     x, y = get_locator_pos(handle)
#     sync_page.sync_input.click("left", x, y)   # type: ignore[attr-defined]
#
#     for modifier_key, js_key in code_for_key.items():
#         sync_page.sync_input.press_keys(modifier_key)   # type: ignore[attr-defined]
#         # sync_page.sync_input._base.browser_window.send_keystrokes("{VK_SHIFT down} bruh")   # type: ignore[attr-defined]
#
#         assert (
#             sync_page.evaluate("() => getResult()")
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
#         sync_page.sync_input.press_keys("!")   # type: ignore[attr-defined]
#         # Shift+! will generate a keypress
#         if js_key[0] == "Shift":
#             assert (
#                 sync_page.evaluate("() => getResult()")
#                 == "Keydown: ! Digit1 49 ["
#                 + js_key[0]
#                 + "]\nKeypress: ! Digit1 33 33 ["
#                 + js_key[0]
#                 + "]"
#             )
#         else:
#             assert (
#                 sync_page.evaluate("() => getResult()")
#                 == "Keydown: ! Digit1 49 [" + js_key[0] + "]"
#             )
#
#         sync_page.sync_input.release_keys("!")   # type: ignore[attr-defined]
#         assert (
#             sync_page.evaluate("() => getResult()")
#             == "Keyup: ! Digit1 49 [" + js_key[0] + "]"
#         )
#         sync_page.sync_input.release_keys(modifier_key)   # type: ignore[attr-defined]
#         assert (
#             sync_page.evaluate("() => getResult()")
#             == "Keyup: "
#             + js_key[0]
#             + " "
#             + js_key[0]
#             + "Left "
#             + js_key[1]
#             + " []"
#         )


def test_quit_exception(sync_page: Page) -> None:
    sync_page.close()
    time.sleep(5)

    with pytest.raises(WindowClosedException):
        sync_page.sync_input.down("left", 100, 100, emulate_behaviour=False)  # type: ignore[attr-defined]
    with pytest.raises(WindowClosedException):
        sync_page.sync_input.up("left", 110, 110)  # type: ignore[attr-defined]
    with pytest.raises(WindowClosedException):
        sync_page.sync_input.move(50, 50, emulate_behaviour=False)  # type: ignore[attr-defined]
    with pytest.raises(WindowClosedException):
        sync_page.sync_input.scroll("up", 10)  # type: ignore[attr-defined]
    with pytest.raises(WindowClosedException):
        sync_page.sync_input.type("test")  # type: ignore[attr-defined]
