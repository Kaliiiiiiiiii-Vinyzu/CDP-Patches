# Sync Usage



## SyncInput

> ### `cdp_patches.input.SyncInput()`

<table><thead><tr><th width="194">Kwargs</th><th width="169">Type</th><th width="269">Usage</th><th>Defaults</th></tr></thead><tbody><tr><td><strong>pid</strong></td><td><code>int</code></td><td><p>The Main Chrome Browser Window PID to connect to. Can also be found in Chromes Task-Manager (Shift+Esc).</p><p></p></td><td><code>None</code></td></tr><tr><td><strong>browser</strong></td><td><code>sync_browsers</code></td><td>A Sync Browser Instance. Can be any of: <br>(sd = selenium_driverless)<br>(pw = playwright)<br>selenium.webdriver.Chrome, sd.sync.webdriver.Chrome,<br>pw.sync_api.Browser, pw.sync_api.BrowserContext</td><td><code>None</code></td></tr><tr><td><strong>scale_factor</strong></td><td><code>float</code></td><td>The Scaling Factor of the Browser. If a <code>browser</code>Instance is passed, this value gets determined automatically.</td><td><code>1.0</code></td></tr><tr><td><strong>emulate_behaviour</strong></td><td><code>bool</code></td><td>Whether to emulate human behaviour.</td><td><code>True</code></td></tr></tbody></table>

***

### SyncInput Properties

<table><thead><tr><th width="194">Property</th><th width="169">Type</th><th width="269">Usage</th><th>Defaults</th></tr></thead><tbody><tr><td><strong>emulate_behaviour</strong></td><td><code>bool</code></td><td>Whether to emulate human behaviour.</td><td><code>True</code></td></tr><tr><td><strong>window_timeout</strong></td><td><code>int</code></td><td><p>The Time of how long to search for the Window in seconds.</p><p></p></td><td><code>30</code></td></tr><tr><td><strong>base</strong></td><td><code>WindowsBase |</code><br><code>LinuxBase</code></td><td>The Base Interaction Layer. Can be useful in some special cases in which emulate_behaviour isnt sufficient. Only Readable.</td><td><code>None</code></td></tr><tr><td><strong>scale_factor</strong></td><td><code>float</code></td><td>The Scaling Factor of the Browser. If a <code>browser</code>Instance is passed, this value gets determined automatically.</td><td><code>1.0</code></td></tr><tr><td><strong>sleep_timeout</strong></td><td><code>float</code></td><td>How long to sleep after certain actions, for example in between a double-click. In Seconds.</td><td><code>0.01</code></td></tr><tr><td><strong>typing_speed</strong></td><td><code>int</code></td><td>How fast to type in WPM.</td><td><code>50</code></td></tr></tbody></table>

***

### SyncInput Methods

{% code fullWidth="true" %}
```python
# Type Abbreviations
Pos = Union[int, float]
Button = Literal["left", "right", "middle"]
EmulateBehaviour: Optional[bool] = True
Timeout: Optional[float] = Non

# Click at the given coordinates with the given button
sync_input.click(button: Button, x: Pos, y: Pos, emulate_behaviour: EmulateBehaviour, timeout: Timeout)

# Double-Click at the given coordinates with the given button
sync_input.double_click(button: Button, x: Pos, y: Pos, emulate_behaviour: EmulateBehaviour, timeout: Timeout)

# Mouse-Down at the given coordinates with the given button
sync_input.down(button: Button, x: Pos, y: Pos, emulate_behaviour: EmulateBehaviour, timeout: Timeout)

# Mouse-Up at the given coordinates with the given button
sync_input.up(button: Button, x: Pos, y: Pos)

# Mouse-Move to the given coordinates
sync_input.move(x: Pos, y: Pos, emulate_behaviour: EmulateBehaviour, timeout: Timeout)

# Scroll the page in the given direction by the given amount
sync_input.scroll(direction: Literal["up", "down", "left", "right"], amount: int)

# Type the given text and optionally fill the input field (Like pasting)
sync_input.type(text: str, fill: Optional[bool] = False, timeout: Timeout)
```
{% endcode %}

