# AIPS Coding Challenge

Submission by Matthieu Herrmann.

The library is in `car_counter.py`, and the application is in `main.py`, which can be launched with
```
python main.py /path/to/file
```

The unit tests (using pytest) are in the `tests` folder, and can be run with
```
python -m pytest
```

## About the task
The task relies on records made of a timestamp T with a time resolution R (of 30 minutes), and a car count C.

> An automated traffic counter sits by a road and counts the number of cars that go
> past. Every half-hour the counter outputs the number of cars seen and resets the counter
> to zero. You are part of a development team that has been asked to implement a system to
> manage this data - the first task required is as follows:
> 
> Write a program that reads a file, where each line contains a timestamp (in yyyy-mm-
> ddThh:mm:ss format, i.e. ISO 8601) for the beginning of a half-hour and the number of
> 
> cars seen that half hour. An example file is included on page 2. You can assume clean
> input, as these files are machine-generated.
> The program should output:
> * The number of cars seen in total
> * A sequence of lines where each line contains a date (in yyyy-mm-dd format) and the
>   number of cars seen on that day (eg. 2016-11-23 289) for all days listed in the input file.
> * The top 3 half hours with most cars, in the same format as the input file
> * The 1.5 hour period with least cars (i.e. 3 contiguous half hour records)

### Competing interpretations of the timestamp meaning
There are two competing interpretations for a timestamp T:

1. "Period" interpretation: the timestamp represents the period R of time preceding itself,
    i.e. the period of time ]T-R, T]. This is the interpretation described in the text above.
2. "Instant" interpretation: the timestamp represents itself.

The second question seems to rely on the second interpretation:
in this case, the first and last timestamps of a date D are `D 00:00:00` and `D 23:30:00`.
On the other hand, with the first interpretation,
the first and last timestamps of a date D are `D 00:30:00` and `D+1 00:00:00`.
This can lead to information loss as `D 00:00:00` would then count for the previous day,
which may not be listed in the file.

Because other questions are unaffected by this issue
(as long as it is understood that the timestamps T represent a time period ]T-R, T]),
I worked with the second interpretation.

### Managing ties
The third and fourth questions ask to pick some records without specifying how to manage ties.
In order not to lose any information, I kept ties, which may lead to more records being returned than asked for.

Note that the ties can have different effect depending on their rank.
Illustrating with letters, picking the top 3:
```
A A B C D E
```
We can pick only 3, i.e. `A A B`

```
A B C C D E
```
We have to pick 4, i.e `A B C C`


## Implementations Notes

The library uses a list of record as its main datastructure.

Records are represented by the `Record` class which contains a timestamp and the associated car count.
Timestamps are represented with python's `datetime.datetime` class, which is used for all time related calculations.
Object of this type can be created by a string.

The car counter is represented by the `CarCounter` class,
which is mainly wrapping a list of records, only ensuring that the list is sorted by timestamp.

The `CarCounter` class comes with static methods general enough to stand on their own:
```python
@staticmethod
def total_count(records: list[Record]) -> int:...

@staticmethod
def group_by_date(records: list[Record]) -> list[list[Record]]:...

@staticmethod
def group_by_contiguity(records: list[Record]) -> list[list[Record]]:...
```

The grouping function expect the input list to be sorted.

The four methods answering the questions are
```python
def get_total_count(self) -> int:...

def get_count_by_date(self) -> list[tuple[str, int]]:...

def get_top_n(self, n: int) -> list[Record]:...

def get_least_period(self, n: int) -> list[list[Record]]:...
```



