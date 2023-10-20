import typing
import os
import subprocess
import sys
from contextlib import closing

IS_POSIX = sys.platform.startswith(("darwin", "cygwin", "linux", "linux2"))

def launch_chrome(args: typing.List[str] = None, binary_path:str=None):
    if binary_path is None:
        binary_path = find_chrome_executable()
    if args is None:
        args = ["--no-first-run", '--disable-component-update', '--no-service-autorun', 
                '--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding',
                '--disable-background-timer-throttling', '--disable-renderer-backgrounding', 
                '--disable-background-networking','--no-pings', '--no-pings', '--disable-infobars', 
                '--disable-breakpad', "--no-default-browser-check", '--homepage=about:blank', '--force-renderer-accessibility']
        if IS_POSIX:
            args.append("--password-store=basic")
        args.append('about:blank')

    process = subprocess.Popen(
                    [binary_path, *args],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=sys.stderr,
                    close_fds=True,
                    preexec_fn=os.setsid if os.name == 'posix' else None,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
                    shell=False,
                    text=True)
    return process

def find_chrome_window(pid:int):
    raise NotImplementedError()

def get_tab(chrome_window, index:int):
    raise NotImplementedError()

def kill_chrome(process, timeout:float=10):
    if os.name == 'posix':
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    else:
        process.terminate()
    try:
         process.wait(timeout)
    except subprocess.TimeoutExpired:
          if os.name == 'posix':
              os.killpg(os.getpgid(process.pid), signal.SIGKILL)
          else:
               process.kill()

def find_chrome_executable() -> str:
     # from https://github.com/ultrafunkamsterdam/undetected-chromedriver/blob/1c704a71cf4f29181a59ecf19ddff32f1b4fbfc0/undetected_chromedriver/__init__.py#L844
    # edited by kaliiiiiiiiii | Aurin Aegerter
    """
    Finds the chrome, chrome beta, chrome canary, chromium executable

    Returns
    -------
    executable_path :  str
        the full file path to found executable

    """
    candidates = set()
    if IS_POSIX:
        for item in os.environ.get("PATH").split(os.pathsep):
            for subitem in (
                    "google-chrome",
                    "chromium",
                    "chromium-browser",
                    "chrome",
                    "google-chrome-stable",
            ):
                candidates.add(os.sep.join((item, subitem)))
        if "darwin" in sys.platform:
            candidates.update(
                [
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "/Applications/Chromium.app/Contents/MacOS/Chromium",
                ]
            )
    else:
        for item in map(
                os.environ.get,
                ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA", "PROGRAMW6432"),
        ):
            if item is not None:
                for subitem in (
                        "Google/Chrome/Application",
                        "Google/Chrome Beta/Application",
                        "Google/Chrome Canary/Application",
                ):
                    candidates.add(os.sep.join((item, subitem, "chrome.exe")))
    for candidate in candidates:
        if os.path.exists(candidate) and os.access(candidate, os.X_OK):
            return os.path.normpath(candidate)