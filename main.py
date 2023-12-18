from pyinput.os_base.windows import BasePointer
from pyinput.utils import find_chrome_window, launch_chrome, kill_chrome

process = launch_chrome()
PID = process.pid

window = find_chrome_window(PID)
# tab = get_tab(window, 0)

pointer = BasePointer(window)
pointer.down(200, 400)

# input("press ENTER to kill")

kill_chrome(process)

