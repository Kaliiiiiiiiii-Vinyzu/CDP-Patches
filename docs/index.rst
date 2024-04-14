Welcome to CDP-Patches!
====================
Installation
------------

Pip
~~~

|PyPI version|

.. code:: bash

   pip install --upgrade pip
   pip install cdp-patches

Initialization
--------------

SyncInput_
~~~~~~~~

-  ``cdp_patches.input.SyncInput()``
..

 Initialize a SyncInput object.

+--------------------------------------+-------------------------------------------+
| Kwargs                               | Usage                                     |
+======================================+===========================================+
| ``pid`` (int)                        | The Main Chrome Browser Window PID        |
|                                      | to connect to. Can also be found in       |
|                                      | Chromes Task-Manager (Shift+Esc)          |
+--------------------------------------+-------------------------------------------+
| ``browser`` (sync_browsers)          | A Sync Browser Instance. Can be any       |
|                                      | of: selenium.webdriver.Chrome,            |
|                                      | selenium_driverless.sync.webdriver.Chrome,|
|                                      | plawright.sync_api.Browser,               |
|                                      | plawright.sync_api.BrowserContext         |
+--------------------------------------+-------------------------------------------+
| ``scale_factor`` (float)             | The Scaling Factor of the Browser.        |
|                                      | Defaults to ``1.0``                       |
+--------------------------------------+-------------------------------------------+
| ``emulate_behaviour`` (bool)         | Wether to emulate human behaviour.        |
|                                      | Defaults to ``True``                      |
+--------------------------------------+-------------------------------------------+
| ``window_timeout`` (float)           | Timeout in seconds to wait for a window to|
|                                      | be found.                                 |
|                                      | Defaults to ``30``                        |
+--------------------------------------+-------------------------------------------+

Methods
~~~~~~~~

-  ``sync_input.click(button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float])``
..

 Click at the given coordinates with the given button

-  ``sync_input.double_click(button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float])``
..

 Double-Click at the given coordinates with the given button

-  ``sync_input.down(button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float])``
..

 Mouse-Down at the given coordinates with the given button

-  ``sync_input.up(button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float])``
..

 Mouse-Up at the given coordinates with the given button

-  ``sync_input.move(x: Union[int, float], y: Union[int, float])``
..

 Mouse-Move to the given coordinates

-  ``sync_input.scroll(direction: Literal["up", "down", "left", "right"], amount: int)``
..

 Scroll the page in the given direction by the given amount

-  ``sync_input.type(text: str, fill: Optional[bool] = False))``
..

 Type the given text and optionally fill the input field (Like pasting)

~~~~~~~~

AsyncInput_
~~~~~~~~

-  ``await cdp_patches.input.AsyncInput()``
..

 Initialize a AsyncInput object.

+--------------------------------------+--------------------------------------+
| Kwargs                               | Usage                                |
+======================================+======================================+
| ``pid`` (int)                        | The Main Chrome Browser Window PID   |
|                                      | to connect to. Can also be found in  |
|                                      | Chromes Task-Manager (Shift+Esc)     |
+--------------------------------------+--------------------------------------+
| ``browser`` (async_browsers)         | An Async Browser Instance. Can be any|
|                                      | of:                                  |
|                                      | selenium_driverless.webdriver.Chrome,|
|                                      | plawright.async_api.Browser,         |
|                                      | plawright.async_api.BrowserContext   |
+--------------------------------------+--------------------------------------+
| ``scale_factor`` (float)             | The Scaling Factor of the Browser.   |
|                                      | Defaults to ``1.0``                  |
+--------------------------------------+--------------------------------------+
| ``emulate_behaviour`` (bool)         | Wether to emulate human behaviour.   |
|                                      | Defaults to ``True``                 |
+--------------------------------------+--------------------------------------+
| ``window_timeout`` (float)           | Timeout in seconds to wait for a w   |
|                                      | indow to be found.                   |
|                                      | Defaults to ``30``                   |
+--------------------------------------+--------------------------------------+

Methods
~~~~~~~~

-  ``await async_input.click(button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float])``
..

 Click at the given coordinates with the given button

-  ``await async_input.double_click(button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float])``
..

 Double-Click at the given coordinates with the given button

-  ``sync_input.down(button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float])``
..

 Mouse-Down at the given coordinates with the given button

-  ``await async_input.up(button: Literal["left", "right", "middle"], x: Union[int, float], y: Union[int, float])``
..

 Mouse-Up at the given coordinates with the given button

-  ``await async_input.move(x: Union[int, float], y: Union[int, float])``
..

 Mouse-Move to the given coordinates

-  ``await async_input.scroll(direction: Literal["up", "down", "left", "right"], amount: int)``
..

 Scroll the page in the given direction by the given amount

-  ``await async_input.type(text: str, fill: Optional[bool] = False))``
..

 Type the given text and optionally fill the input field (Like pasting)
