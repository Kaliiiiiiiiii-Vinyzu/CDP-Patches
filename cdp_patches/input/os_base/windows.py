import re
import warnings
from typing import Literal, Optional

from pywinauto import application
from pywinauto.application import WindowSpecification
from pywinauto.controls.uia_controls import TabControlWrapper, ToolbarWrapper

warnings.filterwarnings("ignore", category=UserWarning, message="32-bit application should be automated using 32-bit Python (you use 64-bit Python)")


class WindowsBase:
    browser_window: WindowSpecification
    hwnd: int
    pid: int
    scale_factor: float = 1.0
    toolbar_height: int = 0
    render_widget_height: int = 0

    def __init__(self, pid: int, scale_factor: float) -> None:
        self.pid = pid
        self.scale_factor = scale_factor

    def get_window(self) -> WindowSpecification:
        win32_app = application.Application(backend="win32")
        win32_app.connect(process=self.pid)

        self.browser_window: WindowSpecification = win32_app.top_window()
        # Perform Window Checks
        self.browser_window.verify_actionable()
        assert self.browser_window.is_normal()

        self._get_renderer_height(self.browser_window)
        return self.browser_window

    def _get_renderer_height(self, window: WindowSpecification) -> None:
        for child in window.iter_children():
            if child.element_info.class_name == "Chrome_RenderWidgetHostHWND":
                self.render_widget_height = child.rectangle().height()

    def _offset_toolbar_height(self) -> None:
        uia_app = application.Application(backend="uia")
        uia_app.connect(process=self.pid)
        top_window = uia_app.top_window()

        def collect_windows(window, tab_control, toolbar):
            for child in window.children():
                if isinstance(child, TabControlWrapper) and not tab_control:
                    tab_control = child
                elif isinstance(child, ToolbarWrapper) and not toolbar:
                    toolbar = child
                tab_control, toolbar = collect_windows(child, tab_control, toolbar)
            return tab_control, toolbar

        tab_control, toolbar = collect_windows(top_window, None, None)

        assert isinstance(tab_control, TabControlWrapper) and isinstance(toolbar, ToolbarWrapper)
        reference_toolbar_height = tab_control.rectangle().height() + toolbar.rectangle().height()
        toolbar_height = top_window.rectangle().height() - self.render_widget_height
        relative_difference = abs(toolbar_height - reference_toolbar_height) / reference_toolbar_height

        if toolbar_height >= reference_toolbar_height and relative_difference < 0.5:
            self.toolbar_height = (reference_toolbar_height + toolbar_height) // 2
        else:
            self.toolbar_height = reference_toolbar_height

    def click(self, button: Literal["left", "right", "middle"], x: int, y: int, double: Optional[bool] = False) -> None:
        y += self.toolbar_height
        self.browser_window.click(button=button, coords=(int(x * self.scale_factor), int(y * self.scale_factor)), double=double)

    def double_click(self, button: Literal["left", "right", "middle"], x: int, y: int) -> None:
        y += self.toolbar_height
        self.click(button=button, x=x, y=y, double=True)

    def down(self, button: Literal["left", "right", "middle"], x: int, y: int) -> None:
        y += self.toolbar_height
        self.browser_window.press_mouse(button=button, coords=(int(x * self.scale_factor), int(y * self.scale_factor)))

    def up(self, button: Literal["left", "right", "middle"], x: int, y: int) -> None:
        y += self.toolbar_height
        self.browser_window.release_mouse(button=button, coords=(int(x * self.scale_factor), int(y * self.scale_factor)))

    def move(self, x: int, y: int) -> None:
        y += self.toolbar_height
        self.browser_window.move_mouse(coords=(int(x * self.scale_factor), int(y * self.scale_factor)), pressed="left")

    def scroll(self, direction: Literal["up", "down", "left", "right"], amount: int) -> None:
        self.browser_window.scroll(direction=direction, amount="line", count=int(amount * self.scale_factor))

    def send_keystrokes(self, text: str) -> None:  # , down: Optional[bool] = False, up: Optional[bool] = False
        # Unmodifying Pywinauto's modifiers & adding down/up modifiers
        modified_text = ""
        selective_regex = re.compile(r"{[^{}]*}|.")

        for key in selective_regex.findall(text):
            # origin_key = key

            if key in ["+", "^", "%", "~"]:
                key = "{" + key + "}"

            # if down or up:
            #     # Note: Only one modifier being used at a time is intentional
            #     modifier = "down" if down else "up"
            #
            #     if "{" in key:
            #         key = key.replace("}", f" {modifier}" + "}")
            #     else:
            #         key = "{" + key + f" {modifier}" + "}"

            # if up and "{" in origin_key:
            #     # Assuming that the key is a modifier
            #     key = origin_key.replace("}", " up}") + key

            modified_text += key

        # if down:
        #     self.press_keys(modified_text)
        # elif up:
        #     self.release_keys(modified_text)
        # else:
        #     self.browser_window.send_keystrokes(modified_text)
        self.browser_window.send_keystrokes(modified_text)

    # def press_keys(self, keystrokes, with_spaces=True, with_tabs=True, with_newlines=True) -> None:
    #     print("WHATTTT THE HELLLLLLLLLLLLLL")
    #     # Edited from https://github.com/pywinauto/pywinauto/blob/atspi/pywinauto/controls/hwndwrapper.py#L483
    #     PBYTE256 = ctypes.c_ubyte * 256
    #
    #     win32gui.SendMessage(self.browser_window.handle, win32con.WM_ACTIVATE,
    #                          win32con.WA_ACTIVE, 0)
    #     target_thread_id = win32functions.GetWindowThreadProcessId(self.browser_window.handle, None)
    #     current_thread_id = win32functions.GetCurrentThreadId()
    #     self.attach_success = win32functions.AttachThreadInput(target_thread_id, current_thread_id, True) != 0
    #     if not self.attach_success:
    #         warnings.warn('Failed to attach app\'s thread to the current thread\'s message queue',
    #                       UserWarning, stacklevel=2)
    #
    #     keyboard_state_stack = [PBYTE256()]
    #     win32functions.GetKeyboardState(keyboard_state_stack[-1])
    #
    #     input_locale_id = win32functions.GetKeyboardLayout(0)
    #     context_code = 0
    #
    #     keys = keyboard.parse_keys(keystrokes, with_spaces, with_tabs, with_newlines)
    #     key_combos_present = any([isinstance(k, keyboard.EscapedKeyAction) for k in keys])
    #     if key_combos_present:
    #         warnings.warn('Key combinations may or may not work depending on the target app',
    #                       UserWarning, stacklevel=2)
    #
    #     try:
    #         for key in keys:
    #             vk, scan, flags = key.get_key_info()
    #
    #             if vk == keyboard.VK_MENU or context_code == 1:
    #                 down_msg, up_msg = win32con.WM_SYSKEYDOWN, win32con.WM_SYSKEYUP
    #             else:
    #                 down_msg, up_msg = win32con.WM_KEYDOWN, win32con.WM_KEYUP
    #
    #             repeat = 1
    #             shift_state = 0
    #             unicode_codepoint = flags & keyboard.KEYEVENTF_UNICODE != 0
    #             if unicode_codepoint:
    #                 char = chr(scan)
    #                 vk_with_flags = win32functions.VkKeyScanExW(char, input_locale_id)
    #                 vk = vk_with_flags & 0xFF
    #                 shift_state = (vk_with_flags & 0xFF00) >> 8
    #                 scan = win32functions.MapVirtualKeyW(vk, 0)
    #
    #             if key.down and vk > 0:
    #                 new_keyboard_state = copy.deepcopy(keyboard_state_stack[-1])
    #
    #                 new_keyboard_state[vk] |= 128
    #                 if shift_state & 1 == 1:
    #                     new_keyboard_state[keyboard.VK_SHIFT] |= 128
    #                 # NOTE: if there are characters with CTRL or ALT in the shift
    #                 # state, make sure to add these keys to new_keyboard_state
    #
    #                 keyboard_state_stack.append(new_keyboard_state)
    #
    #                 lparam = (
    #                         repeat << 0 |
    #                         scan << 16 |
    #                         (flags & 1) << 24 |
    #                         context_code << 29 |
    #                         0 << 31)
    #
    #                 win32functions.SetKeyboardState(keyboard_state_stack[-1])
    #                 win32functions.PostMessage(self.browser_window.handle, down_msg, vk, lparam)
    #                 if vk == keyboard.VK_MENU:
    #                     context_code = 1
    #
    #                 # a delay for keyboard state to take effect
    #                 time.sleep(0.01)
    #
    #     except pywintypes.error as e:
    #         if e.winerror == 1400:
    #             warnings.warn('Application exited before the end of keystrokes',
    #                           UserWarning, stacklevel=2)
    #         else:
    #             warnings.warn(e.strerror, UserWarning, stacklevel=2)
    #         win32functions.SetKeyboardState(keyboard_state_stack[0])
    #
    # def release_keys(self, keystrokes, with_spaces=True, with_tabs=True, with_newlines=True) -> None:
    #     # Edited from https://github.com/pywinauto/pywinauto/blob/atspi/pywinauto/controls/hwndwrapper.py#L483
    #     PBYTE256 = ctypes.c_ubyte * 256
    #
    #     win32gui.SendMessage(self.browser_window.handle, win32con.WM_ACTIVATE,
    #                          win32con.WA_ACTIVE, 0)
    #     target_thread_id = win32functions.GetWindowThreadProcessId(self.browser_window.handle, None)
    #     current_thread_id = win32functions.GetCurrentThreadId()
    #     # attach_success = win32functions.AttachThreadInput(target_thread_id, current_thread_id, True) != 0
    #     # if not attach_success:
    #     #     warnings.warn('Failed to attach app\'s thread to the current thread\'s message queue',
    #     #                   UserWarning, stacklevel=2)
    #     if self.attach_success:
    #         win32functions.AttachThreadInput(target_thread_id, current_thread_id, False)
    #
    #     keyboard_state_stack = [PBYTE256()]
    #     win32functions.GetKeyboardState(keyboard_state_stack[-1])
    #
    #     input_locale_id = win32functions.GetKeyboardLayout(0)
    #     context_code = 0
    #
    #     keys = keyboard.parse_keys(keystrokes, with_spaces, with_tabs, with_newlines)
    #     key_combos_present = any([isinstance(k, keyboard.EscapedKeyAction) for k in keys])
    #     if key_combos_present:
    #         warnings.warn('Key combinations may or may not work depending on the target app',
    #                       UserWarning, stacklevel=2)
    #
    #     try:
    #         for key in keys:
    #             vk, scan, flags = key.get_key_info()
    #
    #             if vk == keyboard.VK_MENU or context_code == 1:
    #                 down_msg, up_msg = win32con.WM_SYSKEYDOWN, win32con.WM_SYSKEYUP
    #             else:
    #                 down_msg, up_msg = win32con.WM_KEYDOWN, win32con.WM_KEYUP
    #
    #             repeat = 1
    #             shift_state = 0
    #             unicode_codepoint = flags & keyboard.KEYEVENTF_UNICODE != 0
    #             if unicode_codepoint:
    #                 char = chr(scan)
    #                 vk_with_flags = win32functions.VkKeyScanExW(char, input_locale_id)
    #                 vk = vk_with_flags & 0xFF
    #                 shift_state = (vk_with_flags & 0xFF00) >> 8
    #                 scan = win32functions.MapVirtualKeyW(vk, 0)
    #
    #             if key.up and vk > 0:
    #                 keyboard_state_stack.pop()
    #
    #                 lparam = (
    #                         repeat << 0 |
    #                         scan << 16 |
    #                         (flags & 1) << 24 |
    #                         context_code << 29 |
    #                         1 << 30 |
    #                         1 << 31)
    #
    #                 win32functions.PostMessage(self.browser_window.handle, up_msg, vk, lparam)
    #                 if keyboard_state_stack:
    #                     win32functions.SetKeyboardState(keyboard_state_stack[-1])
    #
    #                 if vk == keyboard.VK_MENU:
    #                     context_code = 0
    #
    #                 # a delay for keyboard state to take effect
    #                 time.sleep(0.01)
    #
    #     except pywintypes.error as e:
    #         if e.winerror == 1400:
    #             warnings.warn('Application exited before the end of keystrokes',
    #                           UserWarning, stacklevel=2)
    #         else:
    #             warnings.warn(e.strerror, UserWarning, stacklevel=2)
    #         win32functions.SetKeyboardState(keyboard_state_stack[0])
