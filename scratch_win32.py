from pyinput.utils import launch_chrome, kill_chrome
from pywinauto import application
import win32gui, win32con, win32api
import time
from pyinput.os_base.windows import BasePointer, BaseKeyBoard

def click(hwnd:int, x:float, y:float):
    lParam = win32api.MAKELONG(x, y)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, None, lParam)

def get_active_document(window):
    for child in window.iter_children():
        if child.element_info.class_name == 'Chrome_RenderWidgetHostHWND':
            return child

# '--force-renderer-accessibility' flag required
# doesn't work minimized, but background supported
process = launch_chrome()
PID = process.pid

app = application.Application(backend="win32")
app.connect(process=PID)
wins =  app.windows(title_re=r".* - Google Chrome*")

win = wins[0]
doc = get_active_document(win)

p = BasePointer(doc.handle)
k = BaseKeyBoard(doc.handle)
vkey = 	0x41
scan_code = 0x1E
k.down(vkey, scan_code)
k.up(vkey, scan_code)

start = time.monotonic()
for i in range(100):
    click(doc.handle, 100, 100)
print(start - time.monotonic())

kill_chrome(process)

