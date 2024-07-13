import pytest
import subprocess
from cdp_patches.input import SyncInput, AsyncInput


def test_raises_from_pid():
    with pytest.raises(TimeoutError):
        sync_input = SyncInput(pid=-1, window_timeout=1)
        sync_input.click("left", 100, 100)


@pytest.mark.asyncio
async def test_async_raises_from_pid():
    with pytest.raises(TimeoutError):
        sync_input = await AsyncInput(pid=-1, window_timeout=1)
        await sync_input.click("left", 100, 100)


@pytest.mark.asyncio
async def test_async_from_pid(chrome_proc: subprocess.Popen):
    sync_input = await AsyncInput(pid=chrome_proc.pid, window_timeout=1)
    await sync_input.click("left", 100, 100)


def test_sync_from_pid(chrome_proc: subprocess.Popen):
    sync_input = SyncInput(pid=chrome_proc.pid, window_timeout=1)
    sync_input.click("left", 100, 100)
