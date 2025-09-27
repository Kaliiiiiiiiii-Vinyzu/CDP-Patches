import asyncio

import pytest
from selenium_driverless.types.by import By
from selenium_driverless.types.webelement import WebElement
from selenium_driverless.webdriver import Chrome

from cdp_patches.input.exceptions import WindowClosedException
from tests.server import Server

# from input import KeyboardCodes


async def get_locator_pos(locator: WebElement):
    location = await locator.location
    size = await locator.size
    assert location, size

    x, y, width, height = location.get("x"), location.get("y"), size.get("width"), size.get("height")
    assert x and y and width and height

    x, y = x + width // 2, y + height // 2
    return x, y


@pytest.mark.skip("Currently bugged by Driverless. Skipping until Update.")
@pytest.mark.asyncio
async def test_input_leak(async_driver: Chrome, server: Server) -> None:
    await async_driver.get(server.PREFIX + "/input/button.html")
    await async_driver.sleep(1)
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
    assert not is_leaking


@pytest.mark.asyncio
async def test_click_the_button(async_driver: Chrome, server: Server) -> None:
    await async_driver.get(server.PREFIX + "/input/button.html")
    await async_driver.sleep(1)
    sync_locator = await async_driver.find_element(By.XPATH, "//button")
    x, y = await get_locator_pos(sync_locator)
    await async_driver.async_input.click("left", x, y)  # type: ignore[attr-defined]
    assert await async_driver.execute_script("return result") == "Clicked"


@pytest.mark.asyncio
async def test_double_click_the_button(async_driver: Chrome, server: Server) -> None:
    await async_driver.get(server.PREFIX + "/input/button.html")
    await async_driver.sleep(1)
    await async_driver.execute_script(
        """window.double = false;
            button = document.querySelector('button');
            button.addEventListener('dblclick', event => window.double = true);"""
    )

    sync_locator = await async_driver.find_element(By.XPATH, "//button")
    x, y = await get_locator_pos(sync_locator)
    await async_driver.async_input.double_click("left", x, y)  # type: ignore[attr-defined]
    await asyncio.sleep(0.1)
    assert await async_driver.execute_script("return window.double")
    assert await async_driver.execute_script("return result") == "Clicked"


@pytest.mark.asyncio
async def test_locators_hover(async_driver: Chrome, server: Server) -> None:
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
    # sync_page.add_init_script(x)

    await async_driver.get(server.PREFIX + "/input/scrollable.html")
    await async_driver.sleep(1)
    await async_driver.async_input.move(500, 100)  # type: ignore[attr-defined]

    sync_locator = await async_driver.find_element(By.ID, "button-12")
    x, y = await get_locator_pos(sync_locator)
    await async_driver.async_input.move(x, y)  # type: ignore[attr-defined]

    await asyncio.sleep(0.5)
    assert await async_driver.execute_script("return window.last_hover_elem.id") == "button-12"


@pytest.mark.asyncio
async def test_fill_input(async_driver: Chrome, server: Server) -> None:
    await async_driver.get(server.PREFIX + "/input/textarea.html")
    await async_driver.sleep(1)
    sync_locator = await async_driver.find_element(By.XPATH, "//input")
    assert sync_locator

    x, y = await get_locator_pos(sync_locator)
    await async_driver.async_input.click("left", x, y)  # type: ignore[attr-defined]
    await async_driver.async_input.type("some value", fill=True)  # type: ignore[attr-defined]
    assert await async_driver.execute_script("return result") == "some value"


@pytest.mark.asyncio
async def test_keyboard_type_into_a_textarea(async_driver: Chrome) -> None:
    await async_driver.execute_script(
        """
            const textarea = document.createElement('textarea');
            document.body.appendChild(textarea);
            textarea.focus();
        """
    )
    await async_driver.sleep(1)
    text = "Hello world. I +am  the %text that was typed!"

    sync_locator = await async_driver.find_element(By.XPATH, "//textarea")
    assert sync_locator

    x, y = await get_locator_pos(sync_locator)
    await async_driver.async_input.click("left", x, y)  # type: ignore[attr-defined]

    await async_driver.async_input.type(text)  # type: ignore[attr-defined]
    assert await async_driver.execute_script('return document.querySelector("textarea").value') == text


@pytest.mark.asyncio
async def test_quit_exception(async_driver: Chrome) -> None:
    await async_driver.quit()
    await asyncio.sleep(5)

    with pytest.raises(WindowClosedException):
        await async_driver.async_input.down("left", 100, 100, emulate_behaviour=False)
    with pytest.raises(WindowClosedException):
        await async_driver.async_input.up("left", 110, 110)
    with pytest.raises(WindowClosedException):
        await async_driver.async_input.move(50, 50, emulate_behaviour=False)
    with pytest.raises(WindowClosedException):
        await async_driver.async_input.scroll("up", 10)
    with pytest.raises(WindowClosedException):
        await async_driver.async_input.type("test")
