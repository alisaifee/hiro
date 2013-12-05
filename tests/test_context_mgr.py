import os
import unittest
import time
from datetime import datetime, date, timedelta

from hiro import Timeline
from hiro.utils import timedelta_to_seconds
from tests.emulated_modules import sample_1, sample_2


class TestScaledContext(unittest.TestCase):

    def test_accelerate(self):
        s = time.time()
        with Timeline(100):
            time.sleep(10)
        self.assertTrue(time.time() - s < 10)

    def test_deccelerate(self):
        s = time.time()
        with Timeline(0.5):
            time.sleep(0.25)
        self.assertTrue(time.time() - s > 0.25)

    def test_check_time(self):
        start = time.time()
        with Timeline(100):
            last = time.time()
            for i in range(0, 10):
                time.sleep(1)
                delta = time.time() - (start + (i+1)*100)
                self.assertTrue(delta <= 1.5, delta)

    def test_utc(self):
        start_local = datetime.now()
        start_utc = datetime.utcnow()
        with Timeline(50000):
            time.sleep(60*60)
            self.assertEquals( int((datetime.now() - datetime.utcnow()).seconds / 60),
                               int((start_local - start_utc).seconds / 60))
            time.sleep(60*60*23)
            self.assertEquals( (datetime.now() - start_local).days, 1 )
            self.assertEquals( (datetime.utcnow() - start_utc).days, 1 )


class TestTimelineContext(unittest.TestCase):
    def test_forward(self):
        original = date.today()
        with Timeline() as timeline:
            timeline.forward(86400)
            self.assertEquals( (date.today() - original).days, 1)

    def test_rewind(self):
        original_day = date.today()
        original_datetime = datetime.now()
        with Timeline() as timeline:
            timeline.rewind(86400)
            self.assertEquals( (original_day - date.today()).days, 1)
            timeline.forward(timedelta(days=1))
            self.assertEquals( (original_day - date.today()).days, 0)
            timeline.rewind(timedelta(days=1))
            amount = (original_datetime - datetime.now())
            amount_seconds = timedelta_to_seconds(amount)
            self.assertTrue( int(amount_seconds) >= 86399, amount_seconds)

    def test_freeze(self):
        with Timeline() as timeline:
            timeline.freeze()
            originals = sample_1.sub_module_1.sub_sample_1_1_time(), sample_1.sub_module_1.sub_sample_1_1_now()
            time.sleep(1)
            self.assertEquals(time.time(), originals[0])
            self.assertEquals(datetime.now(), originals[1])
        with Timeline() as timeline:
            timeline.freeze()
            originals = sample_2.sub_module_2.sub_sample_2_1_time(), sample_2.sub_module_2.sub_sample_2_1_now()
            time.sleep(1)
            self.assertEquals(time.time(), originals[0])
            self.assertEquals(datetime.now(), originals[1])

    def test_freeze_target(self):
        with Timeline() as timeline:
            timeline.freeze( datetime.fromtimestamp(0) )
            self.assertAlmostEquals(time.time(), 0, 1)

        with Timeline() as timeline:
            timeline.freeze( 0 )
            self.assertAlmostEquals(time.time(), 0, 1)

        with Timeline() as timeline:
            self.assertRaises(TypeError, timeline.freeze, "now")

        with Timeline() as timeline:
            self.assertRaises(AttributeError, timeline.freeze, -1)
            self.assertRaises(AttributeError, timeline.freeze, date(1969,1,1))

    def test_unfreeze(self):
        real_day = date.today()
        with Timeline() as timeline:
            timeline.freeze(0)
            self.assertAlmostEquals(time.time(), 0)
            timeline.unfreeze()
            timeline.scale(10)
            time.sleep(1)
            self.assertAlmostEquals(time.time(), 1.0, 1)
            timeline.forward(timedelta(minutes=2))
            self.assertAlmostEquals(time.time(), 121.0, 1)
            timeline.reset()
            self.assertTrue(int(time.time()) - int(os.popen("date +%s").read().strip()) <= 1)
            timeline.forward(timedelta(days=1))
            self.assertTrue((date.today() - real_day).days == 1)

    def test_freeze_forward_unfreeze(self):

        # start at 2012/12/12 0:0:0
        test_timeline = Timeline(scale=100, start=datetime(2012,12,12,0,0,0))

        # jump forward an hour and freeze
        with test_timeline.forward(60*60).freeze():
            self.assertAlmostEqual((datetime.now() - datetime(2012,12,12,1,0,0)).seconds, 0)
            # sleep 10 seconds
            time.sleep(10)
            # assert no changes
            self.assertAlmostEqual((datetime.now() - datetime(2012,12,12,1,0,0)).seconds, 0)
            # unfreeze timeline
            test_timeline.unfreeze()
            # ensure unfreeze was at the original freeze point
            self.assertAlmostEqual((datetime.now() - datetime(2012,12,12,1,0,0)).seconds, 0)
            # sleep 10 seconds
            time.sleep(10)
            # ensure post unfreeze, time moves
            self.assertAlmostEqual((datetime.now() - datetime(2012,12,12,1,0,0)).seconds, 10)
            # ensure post unfreeze, forward operations work
            test_timeline.forward(timedelta(hours=2))
            self.assertAlmostEqual(int(timedelta_to_seconds(datetime.now() - datetime(2012,12,12,1,0,0))), 60*60*2 + 10)
            # reset everything
            test_timeline.reset()
            self.assertEquals(int(time.time()), int(os.popen("date +%s").read().strip()))



    def test_fluent(self):
        start = datetime.now()
        with Timeline().scale(10).forward(120):
            self.assertTrue(int(timedelta_to_seconds(datetime.now() - start)) >= 120)
            time.sleep(10)
            self.assertTrue(int(timedelta_to_seconds(datetime.now() - start)) >= 130)
        self.assertTrue((datetime.now() - start).seconds < 10)

    def test_decorated(self):
        start = datetime(2013,1,1,0,0,0)
        real_start = datetime.now()
        @Timeline(scale=10, start=start)
        def _decorated():
            time.sleep(10)
            self.assertTrue(int(timedelta_to_seconds(datetime.now() - start)) >= 10)
        _decorated()
        self.assertTrue(((datetime.now() - real_start).seconds < 10))
