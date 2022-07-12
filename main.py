import sys
from car_counter import Record as TS
from car_counter import CarCounter as CC

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("AIPS Coding challenge")
        print("Invoke me with:")
        print("  python main.py <file>")
        exit(0)
    else:
        # Read the input file in a list of timestamp
        timestamp_list = []
        with open(sys.argv[1]) as records:
            for line in records:
                timestamp_list.append(TS.from_string(line))

        # Build a car counter with the list
        cc = CC(timestamp_list)

        # Output
        print(f"Total number of cars: {cc.get_total_count()}")

        print("\nNumber of cars per day:")
        for (date, count) in cc.get_count_by_date():
            print(f"{date} {count}")

        print("\nThe top 3 half hours with most cars (may be longer due to ties):")
        for ts in cc.get_top_n(3):
            print(ts)

        print("\nThe 1.5 hour period with least cars (maybe more than one period due to ties):")
        for period in cc.get_least_period(3):
            print(f"{period[0].timestamp} -- {period[-1].timestamp} {cc.total_count(period)}")

        
