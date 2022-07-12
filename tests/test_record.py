import pytest

from car_counter import Record as REC
from datetime import datetime as DT


def test_Record_parse_string1():
    """
    Must parse a string into a tuple (timestamp, car count)
    """
    timestamp, carcount = REC.parse_string("2021-12-01T05:00:00 5")
    assert (timestamp == DT.fromisoformat("2021-12-01T05:00:00"))
    assert (carcount == int(5))
    with pytest.raises(Exception) as e_info:
        timestamp, carcount = REC.parse_string("2021-12-01T05:00:00 5.5")


def test_Record_from_string():
    """
    Must build a record instance from a string
    """
    ts = REC.from_string("2021-12-01T05:00:00 5")
    assert (ts.timestamp == DT.fromisoformat("2021-12-01T05:00:00"))
    assert (ts.car_count == int(5))


def test_Record_to_string():
    """
    Check that a record can be printed in the expected format, i.e. same as the input format
    """
    ts_string = "2021-12-01T05:00:00 5"
    ts = REC.from_string(ts_string)
    assert (str(ts) == ts_string)


def test_Record_eq():
    """
    Check the equality function between two records
    """
    assert (REC.from_string("2021-12-01T05:00:00 5") == REC.from_string("2021-12-01T05:00:00 5"))
    # Other count
    assert (REC.from_string("2021-12-01T05:00:00 5") != REC.from_string("2021-12-01T05:00:00 50"))
    # Other datetime
    assert (REC.from_string("2021-12-01T05:00:00 5") != REC.from_string("2021-01-01T05:00:00 5"))
    # Other type
    assert (REC.from_string("2021-12-01T05:00:00 5") != 5)
