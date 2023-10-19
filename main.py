from pyinput.base.windows import BasePointer
from pyinput.utils import find_chrome_window, get_tab, launch_chrome, kill_chrome

PID = launch_chrome()

window = find_chrome_window(PID)
tab = get_tab(window, 0)

pointer = BasePointer(tab)
pointer.down(200, 400)

input("press ENTER to kill")
kill_chrome(PID)

