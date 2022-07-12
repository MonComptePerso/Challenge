import datetime
from functools import reduce


class Record:
    """
    A Record associating a timestamp with a car counter.
    """

    def __init__(self, timestamp: datetime.datetime, car_count: int):
        """
        Record constructor

        :param timestamp: When this record has been taken
        :param car_count: The car count associated to this record
        """
        self.timestamp = timestamp
        self.car_count = car_count

    @staticmethod
    def parse_string(string: str) -> tuple[datetime.datetime, int]:
        """
        Parse the string representation of a timestamp and the associated counter into a tuple (datetime, count)

        :param string: The input string with the expected format 'YYYY-MM-DDThh:mm:ss n' where n is the car count
        :return: a tuple (datetime.datetime, int)
        """
        s = string.split(" ")
        timestamp = datetime.datetime.fromisoformat(s[0])
        counter = int(s[1])
        return timestamp, counter

    @staticmethod
    def from_string(string: str):
        """
        Create a record from a string representation

        :param string: The input string with the expected format 'YYYY-MM-DDThh:mm:ss n' where n is the car count
        :return: a Record object
        """
        return Record(*Record.parse_string(string))

    def __str__(self):
        return str(self.timestamp.date()) + "T" + str(self.timestamp.time()) + " " + str(self.car_count)

    def __repr__(self):
        return f"Record({self.timestamp}, {self.car_count})"

    def __eq__(self, other):
        if isinstance(other, Record):
            return self.timestamp == other.timestamp and self.car_count == other.car_count
        else:
            return NotImplemented


class CarCounter:
    """
    Car Counter over periods of time represented by a list of records
    """

    time_resolution: datetime.timedelta = datetime.timedelta(minutes=30)
    """
    Hard coded time resolution (30 minutes) of the counter.
    """

    def __init__(self, records: list[Record]):
        """
        Build a CarCounter with a list of records.
        :param records: a list of record for the car counter.
               The object will store a copy of this list, sorting it by increasing record's timestamp.
        """
        self.records = sorted(records, key=lambda rec: rec.timestamp)

    @staticmethod
    def total_count(records: list[Record]) -> int:
        """
        Count the total number of cars in a list of records

        :param records: Input list of records
        :return: Total number of cars
        """
        return reduce(lambda acc, ts: acc + ts.car_count, records, 0)

    @staticmethod
    def group_by_date(records: list[Record]) -> list[list[Record]]:
        """
        Group the record by date.

        :param records: a list of record. It is assumed that the list is sorted by record's timestamp.
        :return: A list where each item is itself a list of records from the same date.
        """
        if len(records) == 0:
            return []
        else:
            # Main result list: each item is a list of records
            date_list: list[list[Record]] = []

            # Pre-loop
            # Init of the variables using the first record (list is non-empty per above condition)
            same_date_list = [records[0]]  # Sub list of records sharing the same day
            current_date = same_date_list[0].timestamp.date()  # Current date of same_date_list

            # Loop: check if a record 'rec' is from the 'current_date'
            # If so, add it in the same_date_list, else save same_date_list in date_list and create a new list for rec,
            # changing the current_date to its date
            for rec in records[1:]:
                if rec.timestamp.date() == current_date:
                    same_date_list.append(rec)
                else:
                    date_list.append(same_date_list)
                    same_date_list = [rec]
                    current_date = rec.timestamp.date()

            # Post-loop
            # Complete date_list with the last same_date_list
            date_list.append(same_date_list)

        return date_list

    @staticmethod
    def group_by_contiguity(records: list[Record]) -> list[list[Record]]:
        """
        Group contiguous records together.
        Two contiguous records are grouped if they are withing the time resolution of the counter.
        I.E. 2 contiguous timestamps T1 and T2 are grouped if T1 < T2 AND T2 - T1 <= time_resolution

        :param records: a list of record. It is assumed that the list is sorted by record's timestamp.
        :return: A list where each item is itself a list of contiguous records within the time resolution of the counter.
        """
        if len(records) == 0:
            return []
        else:
            # Main result list: each item is a list of records
            result_list: list[list[Record]] = []

            # Pre-loop
            # Init of the variables using the first record (list is non-empty per above condition)
            contiguous_list: list[Record] = [records[0]]  # Current list of contiguous records
            previous = contiguous_list[0].timestamp  # Timestamp of the last record in contiguous_list

            # Loop
            # Extend contiguous_list while the record's timestamp are previous+time_resolution.
            # Save the list and start a new one when a record can't extend it.
            # Always update 'previous' as we progress through the list
            for ts in records[1:]:
                if ts.timestamp - previous <= CarCounter.time_resolution:
                    contiguous_list.append(ts)
                else:
                    result_list.append(contiguous_list)
                    contiguous_list = [ts]
                previous = ts.timestamp

            # Post loop
            # Complete result_list with the last contiguous_list
            result_list.append(contiguous_list)

        return result_list

    def get_total_count(self) -> int:
        """
        Return how many cars have been counted by this counter in total
        :return: Total number of cars
        """
        return CarCounter.total_count(self.records)

    def get_count_by_date(self) -> list[tuple[str, int]]:
        """
        Count the number of car per day (represented as a string yyyy-mm-dd)
        :return: a list of tuples (date as a string, count)
        """
        return list(map(
            lambda l: (str(l[0].timestamp.date()), CarCounter.total_count(l)),
            CarCounter.group_by_date(self.records)
        ))

    def get_top_n(self, n: int) -> list[Record]:
        """
        Get the top n half hours records with the top number of cars.
        Include ties, which may lead to more than n elements.
        :return: a list of records, ordered by record's timestamp, representing the top items
            The list may have less than n elements if n is larger than the number of records
            The list may have more than n elements if ties (records with the same count) exists
        """
        if len(self.records) == 0:
            return []
        elif len(self.records) <= n:
            return self.records.copy()
        else:
            # Create a mapping (car counts->list of records).
            candidates: dict[int, list[Record]] = {}
            for ts in self.records:
                candidates.setdefault(ts.car_count, []).append(ts)

            # Create a new sorted dictionary; sort key (car counts) in decreasing order
            candidates = dict(sorted(candidates.items(), reverse=True))

            # Build the result_list list base on the now sorted candidates
            result_list: list[Record] = []
            for count, timestamps in candidates.items():
                if len(result_list) >= n:
                    break
                else:
                    result_list += timestamps

            # Sort the result_list by timestamp to maintain the format
            return sorted(result_list, key=lambda x: x.timestamp)

    def get_least_period(self, n: int) -> list[list[Record]]:
        """
        Check contiguous periods of n half hours. Return the ones with the least amount of cars.
        Include ties, which may lead to more than one period.
        Shorter periods than 'n' half hours are not counted.
        :return: a list of list, where each inner list represent a period
        """
        if n <= 0 or len(self.records) == 0:
            return []
        else:
            # Only keep contiguous block with enough record
            contiguous = list(filter(lambda l: len(l) >= n, self.group_by_contiguity(self.records)))

            if len(contiguous) == 0:
                return []
            else:
                # Helper function: check one contiguous block B
                # Extract contiguous sub-blocks of length n within B and count the cars.
                # The start of a sub-block is controlled by the "start" parameter
                # Keep the ones (keep ties) with the smallest count in the accumulator "acc"
                def check_block(block: list[Record], start: int, acc: list[tuple[list[Record], int]]):
                    if start + n > len(block):
                        return acc
                    else:
                        sub_block = block[start:start + n]
                        sub_count = self.total_count(sub_block)
                        if sub_count < acc[0][1]:
                            acc = [(sub_block, sub_count)]
                        elif sub_count == acc[0][1]:
                            acc.append((sub_block, sub_count))
                        return check_block(block, start + 1, acc)

                # Init with the first period in the first contiguous block
                init_list = list(contiguous[0][0:n])
                init_count = self.total_count(init_list)

                # Finish the first block, which is our Best So Far (bsf) block
                bsf = check_block(contiguous[0], 1, [(init_list, init_count)])

                # Do the other blocks
                for b in contiguous[1:]:
                    bsf = check_block(b, 0, bsf)

                # Remove counts from the result
                return list(map(lambda list_count: list_count[0], bsf))
