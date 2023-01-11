import math
import os
import time
from datetime import date, datetime, timedelta
from unittest import mock

import pytest

from hiro import Timeline
from hiro.utils import timedelta_to_seconds
from tests.emulated_modules import sample_1, sample_2, sample_3


def test_accelerate():
    s = time.time()
    with Timeline(100):
        time.sleep(10)
    assert time.time() - s < 10


def test_deccelerate():
    s = time.time()
    with Timeline(0.5):
        time.sleep(0.25)
    assert time.time() - s > 0.25


def test_check_time():
    start = time.time()
    with Timeline(100):
        for i in range(0, 10):
            time.sleep(1)
            delta = time.time() - (start + (i + 1) * 100)
            assert delta <= 1.5, delta


def test_utc():
    start_local = datetime.now()
    start_utc = datetime.utcnow()
    with Timeline(100000):
        time.sleep(60 * 60)
        future_diff = (datetime.now() - datetime.utcnow()).seconds / 60.0 / 60.0
        start_diff = (start_local - start_utc).seconds / 60.0 / 60.0
        assert math.ceil(future_diff) == math.ceil(start_diff)

        time.sleep(60 * 60 * 23)
        assert (datetime.now() - start_local).days == 1
        assert (datetime.utcnow() - start_utc).days == 1


def test_forward():
    original = date.today()
    with Timeline() as timeline:
        timeline.forward(86400)
        assert (date.today() - original).days == 1


def test_rewind():
    original_day = date.today()
    original_datetime = datetime.now()
    with Timeline() as timeline:
        timeline.rewind(86400)
        assert (original_day - date.today()).days == 1
        timeline.forward(timedelta(days=1))
        assert (original_day - date.today()).days == 0
        timeline.rewind(timedelta(days=1))
        amount = original_datetime - datetime.now()
        amount_seconds = timedelta_to_seconds(amount)
        assert int(amount_seconds) >= 86399, amount_seconds


def test_freeze():
    with Timeline() as timeline:
        timeline.freeze()
        originals = (
            sample_1.sub_module_1.sub_sample_1_1_time(),
            sample_1.sub_module_1.sub_sample_1_1_now(),
        )
        time.sleep(1)
        assert time.time() == originals[0]
        assert datetime.now() == originals[1]
    with Timeline() as timeline:
        timeline.freeze()
        originals = (
            sample_2.sub_module_2.sub_sample_2_1_time(),
            sample_2.sub_module_2.sub_sample_2_1_now(),
        )
        time.sleep(1)
        assert time.time() == originals[0]
        assert datetime.now() == originals[1]
    with Timeline() as timeline:
        timeline.freeze()
        originals = (
            sample_3.sub_module_3.sub_sample_3_1_time(),
            sample_3.sub_module_3.sub_sample_3_1_now(),
            sample_3.sub_module_3.sub_sample_3_1_gmtime(),
        )
        time.sleep(1)
        assert time.time() == originals[0]
        assert datetime.now() == originals[1]
        assert time.gmtime() == originals[2]


def test_freeze_target():
    with Timeline() as timeline:
        timeline.freeze(datetime.fromtimestamp(0))
        assert round(abs(time.time() - 0), 1) == 0

    with Timeline() as timeline:
        timeline.freeze(0)
        assert round(abs(time.time() - 0), 1) == 0
        assert round(abs(time.time_ns() - 0), 1) == 0
        assert round(abs(time.monotonic() - 0), 1) == 0
        assert round(abs(time.monotonic_ns() - 0), 1) == 0

    with Timeline() as timeline:
        with pytest.raises(TypeError):
            timeline.freeze("now")

    with Timeline() as timeline:
        with pytest.raises(AttributeError):
            timeline.freeze(-1)
        with pytest.raises(AttributeError):
            timeline.freeze(date(1969, 1, 1))


def test_unfreeze():
    real_day = date.today()
    with Timeline() as timeline:
        timeline.freeze(0)
        assert round(abs(time.time() - 0), 7) == 0
        timeline.unfreeze()
        timeline.scale(10)
        time.sleep(1)
        assert int(time.time()) == 1
        timeline.forward(timedelta(minutes=2))
        assert int(time.time()) == 121
        timeline.reset()
        assert (int(time.time()) - int(os.popen("date +%s").read().strip())) <= 1
        timeline.forward(timedelta(days=1))
        assert (date.today() - real_day).days == 1


def test_freeze_forward_unfreeze():

    # start at 2012/12/12 0:0:0
    test_timeline = Timeline(scale=100, start=datetime(2012, 12, 12, 0, 0, 0))

    # jump forward an hour and freeze
    with test_timeline.forward(60 * 60).freeze():
        assert (
            round(
                abs((datetime.now() - datetime(2012, 12, 12, 1, 0, 0)).seconds - 0), 7
            )
            == 0
        )
        # sleep 10 seconds
        time.sleep(10)
        # assert no changes
        assert (
            round(
                abs((datetime.now() - datetime(2012, 12, 12, 1, 0, 0)).seconds - 0), 7
            )
            == 0
        )
        # unfreeze timeline
        test_timeline.unfreeze()
        # ensure unfreeze was at the original freeze point
        assert (
            round(
                abs((datetime.now() - datetime(2012, 12, 12, 1, 0, 0)).seconds - 0), 7
            )
            == 0
        )
        # sleep 10 seconds
        time.sleep(10)
        # ensure post unfreeze, time moves
        assert (datetime.now() - datetime(2012, 12, 12, 1, 0, 0)).seconds >= 10

        # ensure post unfreeze, forward operations work
        test_timeline.forward(timedelta(hours=2))
        assert (
            int((datetime.now() - datetime(2012, 12, 12, 1, 0, 0)).seconds / 3600) == 2
        )
        # reset everything
        test_timeline.reset()
        assert int(time.time()) == int(os.popen("date +%s").read().strip())


def test_fluent():
    start = datetime.now()
    with Timeline().scale(10).forward(120):
        assert int(timedelta_to_seconds(datetime.now() - start)) >= 120
        time.sleep(10)
        assert int(timedelta_to_seconds(datetime.now() - start)) >= 130
    assert (datetime.now() - start).seconds < 10


def test_decorated():
    start = datetime(2013, 1, 1, 0, 0, 0)
    real_start = datetime.now()

    @Timeline(scale=10, start=start)
    def _decorated():
        time.sleep(10)
        assert int(timedelta_to_seconds(datetime.now() - start)) >= 10

    _decorated()
    assert (datetime.now() - real_start).seconds < 10


def test_decorated_with_argument():
    @Timeline()
    def _decorated(timeline):
        assert isinstance(timeline, Timeline)

    _decorated()

    @Timeline()
    def _decorated(timeline=None):
        assert isinstance(timeline, Timeline)

    _decorated()


def test_decorated_exception():
    class SomeException(Exception):
        pass

    @Timeline()
    def _decorated():
        raise SomeException("asdf")

    with pytest.raises(SomeException):
        _decorated()


@mock.patch("hiro.core.IGNORED_MODULES", new_callable=set)
def test_patch_ignored_modules(IGNORED_MODULES):
    hiro_dummy_module = mock.MagicMock(__dir__=mock.MagicMock(side_effect=Exception))

    with mock.patch.dict("sys.modules", {"hiro_dummy_module": hiro_dummy_module}):
        with Timeline().freeze():
            pass

        with Timeline().freeze():
            pass

        hiro_dummy_module.__dir__.assert_called_once()
        assert hiro_dummy_module in IGNORED_MODULES
