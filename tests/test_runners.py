"""

"""
import unittest
import time
import hiro
from hiro.errors import SegmentNotComplete


class TestSyncRunner(unittest.TestCase):
    def test_scale_up_runner(self):
        def _slow_func():
            time.sleep(1)
            return 1
        f = hiro.run_sync(4, _slow_func)
        self.assertTrue(f.get_execution_time() < 1)
        self.assertEquals(f.get_response(), 1)


    def test_scale_up_runner_fail(self):
        def _slow_func():
            time.sleep(1)
            raise Exception("foo")
        f = hiro.run_sync(4, _slow_func)
        self.assertRaises(Exception, f.get_response)
        self.assertTrue(f.get_execution_time() < 1)


class TestASyncRunner(unittest.TestCase):
    def test_scale_up_runner(self):
        def _slow_func():
            time.sleep(1)
        f = hiro.run_async(4, _slow_func)
        self.assertTrue(f.is_running())
        f.join()
        self.assertTrue(f.get_execution_time() < 1)


    def test_scale_up_runner_fail(self):
        def _slow_func():
            time.sleep(1)
            raise Exception("foo")
        f = hiro.run_async(4, _slow_func)
        self.assertTrue(f.is_running())
        f.join()
        self.assertRaises(Exception, f.get_response)
        self.assertTrue(f.get_execution_time() < 1)

    def test_segment_not_complete_error(self):
        def _slow_func():
            time.sleep(1)
            raise Exception("foo")
        f = hiro.run_async(4, _slow_func)
        self.assertRaises(SegmentNotComplete, f.get_execution_time)
        self.assertRaises(SegmentNotComplete, f.get_response)
        self.assertTrue(f.is_running())
        f.join()
        self.assertRaises(Exception, f.get_response)
        self.assertTrue(f.get_execution_time() < 1 )
