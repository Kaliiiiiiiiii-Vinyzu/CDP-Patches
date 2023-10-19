import typing
def find_chrome_window(pid:int):
    raise NotImplementedError()

def get_tab(chrome_window, index:int):
    raise NotImplementedError()

def launch_chrome(path:str, args:typing.List[str]=None) -> int
    """
    returns PID of process
    """
    raise NotImplementedError()

def kill_chrome(pid:int):
    raise NotImplementedError()

def find_chrome_path() -> str:
    raise NotImplementedError()