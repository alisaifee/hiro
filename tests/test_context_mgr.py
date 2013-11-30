from decimal import Decimal
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
            last = Decimal(time.time())
            for i in range(0, 10):
                time.sleep(1)
                self.assertAlmostEquals(time.time(), start + ((i+1)*100), delta=1.5)



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
            self.assertAlmostEquals( (original_datetime - datetime.now()).total_seconds(), 86400, 1)

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
        start = time.time()
        with Timeline() as timeline:
            timeline.freeze(0)
            self.assertAlmostEquals(time.time(), 0)
            timeline.unfreeze()
            timeline.scale(10)
            self.assertTrue(time.time() - start > 0, time.time() - start)
            time.sleep(1)
            self.assertTrue(time.time() - start > 10, time.time() - start)

