from pyinput.utils import launch_chrome, kill_chrome
from pywinauto import application

process = launch_chrome()
PID = process.pid


app = application.Application()
app.connect(process=PID)
dlg = app.top_window_()
dlg.PrintControlIdentifiers()
renderer = dlg.Chrome_RenderWidgetHostHWND

# input("press ENTER to kill")

kill_chrome(process)

