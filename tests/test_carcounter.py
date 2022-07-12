import datetime
import pytest

from car_counter import Record as TS
from car_counter import CarCounter as CC


#
# Fixtures
#
# We use the seek files and 3 custom dataset

@pytest.fixture
def record_seek():
    """
    Seek fixture (provided list of records)
    Group by day: [179, 81, 134, 4]
    Total: 398
    :return: list of records
    """
    records_list = []
    with open("tests/fixtures/record_seek.txt") as records:
        for line in records:
            records_list.append(TS.from_string(line))
    assert (len(records_list) == 24)
    return records_list


@pytest.fixture
def record_oneday():
    """
    Fixture with 3 consecutive records over the same day, with a total of [5, 15, 30] = 50 cars
    :return: list of records
    """
    return [
        TS.from_string("2021-12-01T05:00:00 5"),
        TS.from_string("2021-12-01T05:30:00 15"),
        TS.from_string("2021-12-01T06:00:00 30"),
    ]


@pytest.fixture
def record_onemonth():
    """
    Fixture with 6 records over the same day number, but different months with a total of 2*(5 + 15 + 30) = 100 cars
    :return: list of records over two days, 3 contiguous the first day, 2 contiguous and 1 separated the second day
    """
    return [
        TS.from_string("2021-11-01T05:00:00 5"),
        TS.from_string("2021-11-01T05:30:00 15"),
        TS.from_string("2021-11-01T06:00:00 30"),
        TS.from_string("2021-12-01T10:00:00 5"),
        TS.from_string("2021-12-01T10:30:00 15"),
        TS.from_string("2021-12-01T12:00:00 30"),
    ]


@pytest.fixture
def record_newyear():
    """
    Fixture with 6 consecutive records over a new year, with  30 + 15 + 5 + 5 + 15 + 30 = 100 cars
    :return: list of records
    """
    return [
        TS.from_string("2021-12-31T22:30:00 30"),
        TS.from_string("2021-12-31T23:00:00 15"),
        TS.from_string("2021-12-31T23:30:00 5"),
        TS.from_string("2022-01-01T00:00:00 5"),
        TS.from_string("2022-01-01T00:30:00 15"),
        TS.from_string("2022-01-01T01:00:00 30"),
    ]



def test_CC_total_count(record_oneday, record_onemonth, record_seek):
    """
    Given a list of records, compute the total number of cars
    """
    assert (CC.total_count([]) == 0)
    assert (CC.total_count(record_oneday) == 50)
    assert (CC.total_count(record_onemonth) == 100)
    assert (CC.total_count(record_seek) == 398)


def test_CC_get_total_count(record_oneday, record_onemonth, record_seek):
    """
    Check the get_total_count method
    """
    assert (CC([]).get_total_count() == 0)
    assert (CC(record_oneday).get_total_count() == 50)
    assert (CC(record_onemonth).get_total_count() == 100)
    assert (CC(record_seek).get_total_count() == 398)


def test_CC_group_by_date(record_oneday, record_onemonth, record_seek):
    """
    Given a list of records, group them by date
    """
    assert (len(CC.group_by_date([])) == 0)
    #
    by_day = CC.group_by_date(record_oneday)
    assert (len(by_day) == 1)
    assert (list(map(CC.total_count, by_day)) == [50])
    #
    by_month = CC.group_by_date(record_onemonth)
    assert (len(by_month) == 2)
    assert (list(map(CC.total_count, by_month)) == [50, 50])
    #
    seek = CC.group_by_date(record_seek)
    assert (len(seek) == 4)
    assert (list(map(CC.total_count, seek)) == [179, 81, 134, 4])


def test_CC_get_count_by_date(record_oneday, record_onemonth, record_seek):
    """
    Count the number of cars per date
    """
    assert (CC([]).get_count_by_date() == [])
    assert (CC(record_oneday).get_count_by_date() == [("2021-12-01", 50)])
    assert (CC(record_onemonth).get_count_by_date() == [("2021-11-01", 50), ("2021-12-01", 50)])
    assert (CC(record_seek).get_count_by_date() == [
        ("2021-12-01", 179), ("2021-12-05", 81), ("2021-12-08", 134), ("2021-12-09", 4)]
            )


def test_CC_get_top_n(record_oneday, record_seek):
    """
    Get the top n half hours with most cars
    """
    assert (CC([]).get_top_n(0) == [])
    assert (CC([]).get_top_n(1) == [])

    # Given that one day has 3 items, test the [0, 1, 2] range, and beyond [3, 4]
    assert (CC(record_oneday).get_top_n(0) == [])
    assert (CC(record_oneday).get_top_n(1) == [record_oneday[2]])
    assert (CC(record_oneday).get_top_n(2) == [record_oneday[1], record_oneday[2]])
    assert (CC(record_oneday).get_top_n(3) == record_oneday)
    assert (CC(record_oneday).get_top_n(4) == record_oneday)

    # Test on seek with 3, manually picking the top timestamps
    assert (CC(record_seek).get_top_n(3) == list(
        map(TS.from_string, ["2021-12-01T07:30:00 46", "2021-12-01T08:00:00 42", "2021-12-08T18:00:00 33"])))

    # Test with ties: we potentially want more than 3
    def ts(hour: int, count: int):
        """ Helper function to generate timestamps string at a predefined day, but parameterized hour """
        return TS(datetime.datetime.fromisoformat(f"2021-12-01T{hour:02d}:00:00"), count)

    # Ties at the top count: ask 1 but get 3
    list1 = [ts(0, 50), ts(1, 50), ts(2, 50), ts(3, 15), ts(4, 10), ts(5, 5)]
    assert (CC(list1).get_top_n(0) == [])
    assert (CC(list1).get_top_n(1) == [ts(0, 50), ts(1, 50), ts(2, 50)])

    # Ties at the bottom of the range: ask 3 but get 4
    list2 = [ts(0, 50), ts(1, 40), ts(2, 30), ts(3, 30), ts(4, 5), ts(5, 0)]
    assert (CC(list2).get_top_n(3) == [ts(0, 50), ts(1, 40), ts(2, 30), ts(3, 30)])

    # Ties on seek when n = 5 (last count at 25)
    assert (CC(record_seek).get_top_n(5) == list(
        map(TS.from_string, [
            "2021-12-01T07:00:00 25",
            "2021-12-01T07:30:00 46",
            "2021-12-01T08:00:00 42",
            "2021-12-08T18:00:00 33",
            "2021-12-08T19:00:00 28",
            "2021-12-08T20:00:00 25"
        ])))


def test_CC_group_by_contiguity(record_oneday, record_onemonth, record_newyear):
    """
    Given a list of timestamps, group them by contiguity
    """
    assert (len(CC.group_by_contiguity([])) == 0)
    # One contiguous day
    by_day = CC.group_by_contiguity(record_oneday)
    assert (len(by_day) == 1)
    assert (list(map(CC.total_count, by_day)) == [50])
    # One contiguous day and a splited day in 2, for a total of 3 "blocks"
    by_month = CC.group_by_contiguity(record_onemonth)
    assert (len(by_month) == 3)
    assert (list(map(CC.total_count, by_month)) == [50, 20, 30])
    # One contiguous block spanning a new year
    new_year = CC.group_by_contiguity(record_newyear)
    assert (len(new_year) == 1)
    assert (list(map(CC.total_count, new_year)) == [100])


def test_CC_get_least_period(record_oneday, record_onemonth, record_seek, record_newyear):
    """
    Find a period of time with the least amount of car
    """
    assert (CC([]).get_least_period(0) == [])
    assert (CC([]).get_least_period(1) == [])
    # Test on one contiguous day. If the range is too large, we must have an empty list.
    assert (CC(record_oneday).get_least_period(0) == [])
    assert (CC(record_oneday).get_least_period(1) == [[TS.from_string("2021-12-01T05:00:00 5")]])
    assert (CC(record_oneday).get_least_period(2) == [
        [TS.from_string("2021-12-01T05:00:00 5"), TS.from_string("2021-12-01T05:30:00 15")]
    ])
    assert (CC(record_oneday).get_least_period(4) == [])
    # We have ties on onemonth
    assert (CC(record_onemonth).get_least_period(2) == [
        [TS.from_string("2021-11-01T05:00:00 5"), TS.from_string("2021-11-01T05:30:00 15")],
        [TS.from_string("2021-12-01T10:00:00 5"), TS.from_string("2021-12-01T10:30:00 15")]
    ])
    # Hand pick period of 3 on seek record
    assert (CC(record_seek).get_least_period(3) == [[
        TS.from_string("2021-12-01T05:00:00 5"),
        TS.from_string("2021-12-01T05:30:00 12"),
        TS.from_string("2021-12-01T06:00:00 14")
    ]])
    # Check spanning a day/month/year
    assert (CC(record_newyear).get_least_period(2) == [
        [TS.from_string("2021-12-31T23:30:00 5"), TS.from_string("2022-01-01T00:00:00 5")]
    ])
