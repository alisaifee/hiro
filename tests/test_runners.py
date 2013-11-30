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
        self.assertAlmostEquals(f.real_execution_time(), 0.25, 1)
        self.assertEquals(f.response(), 1)


    def test_scale_up_runner_fail(self):
        def _slow_func():
            time.sleep(1)
            raise Exception("foo")
        f = hiro.run_sync(4, _slow_func)
        self.assertRaises(Exception, f.response)
        self.assertAlmostEquals(f.real_execution_time(), 0.25, 1)


class TestASyncRunner(unittest.TestCase):
    def test_scale_up_runner(self):
        def _slow_func():
            time.sleep(1)
        f = hiro.run_async(4, _slow_func)
        self.assertTrue(f.is_running())
        f.join()
        self.assertAlmostEquals(f.real_execution_time(), 0.25, 1)


    def test_scale_up_runner_fail(self):
        def _slow_func():
            time.sleep(1)
            raise Exception("foo")
        f = hiro.run_async(4, _slow_func)
        self.assertTrue(f.is_running())
        f.join()
        self.assertRaises(Exception, f.response)
        self.assertAlmostEquals(f.real_execution_time(), 0.25, 1)

    def test_segment_not_complete_error(self):
        def _slow_func():
            time.sleep(1)
            raise Exception("foo")
        f = hiro.run_async(4, _slow_func)
        self.assertRaises(SegmentNotComplete, f.real_execution_time)
        self.assertRaises(SegmentNotComplete, f.response)
        self.assertTrue(f.is_running())
        f.join()
        self.assertRaises(Exception, f.response)
        self.assertAlmostEquals(f.real_execution_time(), 0.25, 1)
