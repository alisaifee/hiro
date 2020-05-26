"""

"""
import time
import hiro
from hiro.errors import SegmentNotComplete
import pytest


def test_scale_up_sync_runner():
    def _slow_func():
        time.sleep(1)
        return 1
    f = hiro.run_sync(4, _slow_func)
    assert f.get_execution_time() < 1
    assert f.get_response() == 1


def test_scale_up_sync_runner_fail():
    def _slow_func():
        time.sleep(1)
        raise Exception("foo")
    f = hiro.run_sync(4, _slow_func)
    with pytest.raises(Exception):
        f.get_response()
    assert f.get_execution_time() < 1


def test_scale_up_async_runner():
    def _slow_func():
        time.sleep(1)
    f = hiro.run_async(4, _slow_func)
    assert f.is_running()
    f.join()
    assert f.get_execution_time() < 1


def test_scale_up_async_runner_fail():
    def _slow_func():
        time.sleep(1)
        raise Exception("foo")
    f = hiro.run_async(4, _slow_func)
    assert f.is_running()
    f.join()
    with pytest.raises(Exception):
        f.get_response()
    assert f.get_execution_time() < 1


def test_segment_not_complete_error():
    def _slow_func():
        time.sleep(1)
        raise Exception("foo")
    f = hiro.run_async(4, _slow_func)
    with pytest.raises(SegmentNotComplete):
        f.get_execution_time()
    with pytest.raises(SegmentNotComplete):
        f.get_response()
    assert f.is_running()
    f.join()
    with pytest.raises(Exception):
        f.get_response()
    assert f.get_execution_time() < 1
