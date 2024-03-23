import pytest
from playwright.async_api import Locator, Page

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
    assert await async_page.evaluate("double")
    assert await async_page.evaluate("result") == "Clicked"


@pytest.mark.asyncio
async def test_locators_hover(async_page: Page, server: Server) -> None:
    # x = """window.addEventListener("DOMContentLoaded",()=>{function highest_z_idx(){const allElements=document.querySelectorAll("*");let highestZIndex=0;allElements.forEach((element)=>{const
    #     zIndex=parseInt(getComputedStyle(element).zIndex,10);if(zIndex&&zIndex>highestZIndex){highestZIndex=zIndex}});return highestZIndex}function round_2(num){return Math.round((
    #     num+Number.EPSILON)*100)/100}z_idx=highest_z_idx();const canvas=document.createElement("canvas");canvas.style.position="fixed";canvas.style.top="0";canvas.style.left="0";canvas.style.zIndex=
    #     String(z_idx+1);canvas.width=window.innerWidth;canvas.height=window.innerHeight;canvas.style.pointerEvents="none";const clearButton=document.createElement("button");clearButton.textContent=
    #     "Clear";clearButton.style.position="fixed";clearButton.style.top="10px";clearButton.style.left="10px";clearButton.id="clear";clearButton.style.zIndex=String(z_idx+2);clearButton.style.opacity=
    #     "0.7";const tab=document.createElement("div");tab.style.position="fixed";tab.style.top="10px";tab.style.right="10px";tab.style.padding="5px 10px";tab.style.borderRadius="5px";
    #     tab.style.pointerEvents="none";tab.style.fontFamily="Arial, sans-serif";tab.style.fontSize="14px";tab.style.fontWeight="bold";tab.style.zIndex=String(z_idx+3);tab.style.opacity="0.8";
    #     tab.textContent="average ClickDeltaTime: 0.00ms +/-0.00,Average Frequency: 0.00 Hz, count:0, x:0, y:0";const graphCanvas=document.createElement("canvas");graphCanvas.width=window.innerWidth;
    #     graphCanvas.height=200;graphCanvas.style.position="fixed";graphCanvas.style.bottom="0";graphCanvas.style.left="0";graphCanvas.style.zIndex=String(z_idx+4);graphCanvas.style.pointerEvents=
    #     "None";const ctx=canvas.getContext("2d");let lastEventTime=0;let timeSinceClear=0;let timeDeltaData=[];let mousedownTime=0;let clickdeltaTimes=[];let averageClickDeltaTime=0;
    #     click_delta_max_diff=0;function plot_point(x,y,color="red",radius="2",opacity=0.5){ctx.fillStyle=color;ctx.globalAlpha=opacity;ctx.beginPath();ctx.arc(x,y,radius,0,Math.PI*2);ctx.fill();
    #     ctx.globalAlpha=1;}function clear(){ctx.clearRect(0,0,canvas.width,canvas.height);lastEventTime=0;timeSinceClear=0;timeDeltaData=[];let mousedownTime=0;let clickdeltaTimes=[];
    #     let averageClickDeltaTime=0;click_delta_max_diff=0;tab.textContent="average ClickDeltaTime: 0.00ms +/-0.00, Average Frequency: 0.00 Hz, count:0, x:0, y:0"};function updateCanvasDimensions()
    #     {canvas.width=window.innerWidth;canvas.height=window.innerHeight;graphCanvas.width=window.innerWidth;drawTimeDeltaGraph()}function drawTimeDeltaGraph(){const graphCtx=
    #     graphCanvas.getContext("2d");graphCtx.clearRect(0,0,graphCanvas.width,graphCanvas.height);graphCtx.globalAlpha=0.3;graphCtx.fillStyle="white";graphCtx.fillRect(0,0,graphCanvas.width,
    #     graphCanvas.height);graphCtx.globalAlpha=1;graphCtx.fillStyle="black";if(timeDeltaData.length>graphCanvas.width){timeDeltaData.splice(0,timeDeltaData.length-graphCanvas.width)}
    #     const maxTimeDelta=Math.max(...timeDeltaData);const scaleFactor=graphCanvas.height/maxTimeDelta;const gridSpacing=20;graphCtx.strokeStyle="black";graphCtx.beginPath();for(let y=0;y<=
    #     graphCanvas.height;y+=gridSpacing){graphCtx.moveTo(0,y);graphCtx.lineTo(graphCanvas.width,y);const timeValue=(maxTimeDelta*(graphCanvas.height-y)/graphCanvas.height).toFixed(2);
    #     if(isFinite(timeValue)){graphCtx.fillText(timeValue+" ms",graphCanvas.width-50,y+12)}}graphCtx.stroke();graphCtx.beginPath();graphCtx.strokeStyle="black";graphCtx.moveTo(0,0);
    #     graphCtx.lineTo(graphCanvas.width,0);graphCtx.stroke();graphCtx.beginPath();graphCtx.strokeStyle="black";graphCtx.moveTo(0,graphCanvas.height);graphCtx.lineTo(graphCanvas.width,
    #     graphCanvas.height);graphCtx.stroke();graphCtx.beginPath();graphCtx.strokeStyle="green";graphCtx.moveTo(0,graphCanvas.height-timeDeltaData[0]*scaleFactor);for(let i=1;i<
    #     timeDeltaData.length;i+=1){graphCtx.lineTo(i,graphCanvas.height-timeDeltaData[i]*scaleFactor)}graphCtx.stroke();graphCtx.fillStyle="black";graphCtx.font="12px Arial";
    #     graphCtx.fillText("0 ms",2,graphCanvas.height-2);graphCtx.fillText(`${timeDeltaData.length-1} ms`,graphCanvas.width-30,graphCanvas.height-2);graphCtx.fillText(`${maxTimeDelta.toFixed(2)} ms`
    #     ,2,10)}function move_handler(event){const currentTime=Date.now();const delta=currentTime-lastEventTime;const x=event.x;const y=event.y;if(delta<=100){if(lastEventTime!==0){timeSinceClear+=
    #     delta;timeDeltaData.push(delta);const averageDelta=timeDeltaData.length===0?0:timeDeltaData.reduce((sum,value)=>sum+value)/timeDeltaData.length;const frequency=averageDelta===0?0:1000/
    #     averageDelta;tab.textContent=`average ClickDeltaTime: ${ averageClickDeltaTime }ms +/-${ click_delta_max_diff }, Average Frequency: ${frequency.toFixed(2)} Hz, count:${timeDeltaData.length }
    #     ,x:${ x }, y:${ y }`;drawTimeDeltaGraph()}}lastEventTime=currentTime;plot_point(x,y)}function click_handler(e){plot_point(e.x,e.y,"green",5)};function mouseup_handler(){const mouseupTime=
    #     Date.now();const deltaTime=mouseupTime-mousedownTime;clickdeltaTimes.push(deltaTime);delta_average=clickdeltaTimes.reduce((sum,time)=>sum+time,
    #     0)/clickdeltaTimes.length;click_delta_max_diff=round_2(((Math.max(...clickdeltaTimes)-delta_average)+(delta_average-Math.min(...clickdeltaTimes)))/2);averageClickDeltaTime=
    #     round_2(delta_average)}document.body.appendChild(canvas);document.body.appendChild(graphCanvas);document.addEventListener("mousemove",move_handler);document.addEventListener("click",
    #     click_handler);document.addEventListener("mousedown",(e)=>{mousedownTime=Date.now()});document.body.appendChild(tab);window.addEventListener("resize",updateCanvasDimensions);
    #     document.body.appendChild(clearButton);clearButton.addEventListener("click",clear);updateCanvasDimensions();document.addEventListener("mouseup",mouseup_handler);})"""
    # await async_page.add_init_script(x)

    await async_page.goto(server.PREFIX + "/input/scrollable.html")
    await async_page.async_input.move(500, 100)  # type: ignore[attr-defined]

    button = async_page.locator("#button-12")
    x, y = await get_locator_pos(button)
    await async_page.async_input.move(x, y)  # type: ignore[attr-defined]

    assert await async_page.evaluate("document.querySelector('button:hover').id") == "button-12"


@pytest.mark.skip(reason="Scrolling is discouraged")
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
