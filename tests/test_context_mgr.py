import os
import unittest
import time
from datetime import datetime, date, timedelta

from hiro import Timeline
from hiro.core import ScaledTimeline
from tests.emulated_modules import sample_1, sample_2


class TestScaledContext(unittest.TestCase):

    def test_accelerate(self):
        s = time.time()
        with ScaledTimeline(100,None):
            time.sleep(10)
        self.assertAlmostEquals(time.time() - s, 0.1, 1)

    def test_deccelerate(self):
        s = time.time()
        with ScaledTimeline(0.5,None):
            time.sleep(0.25)
        self.assertAlmostEquals(time.time() - s, 0.5, 1)

    def test_check_time(self):
        start = time.time()
        with ScaledTimeline(100, None):
            last = time.time()
            for i in range(0, 10):
                time.sleep(1)
                delta = time.time() - (start + (i+1)*100)
                self.assertTrue(delta <= 1.5, delta)

    def test_utc(self):
        start_local = datetime.now()
        start_utc = datetime.utcnow()
        with ScaledTimeline(50000):
            time.sleep(60*60)
            self.assertEquals( (datetime.now() - datetime.utcnow()).seconds / 60,
                               (start_local - start_utc).seconds / 60)
            print "pre"
            time.sleep(60*60*23)
            print "post"
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
            amount_seconds = float(amount.microseconds + (amount.seconds + amount.days * 24 * 3600) * 10**6) / 10**6
            self.assertAlmostEquals( amount_seconds, 86400, 1 )

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
            self.assertRaises(AttributeError, timeline.freeze, "now")

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
            self.assertEquals(int(time.time()), int(os.popen("date +%s").read().strip()))
            timeline.forward(timedelta(days=1))
            self.assertTrue((date.today() - real_day).days == 1)

