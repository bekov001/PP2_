import datetime
import timedelta


# 1
current_date = datetime.date.today()
five_days_ago = current_date - timedelta(days=5)
print(f"Five days ago: {five_days_ago}")


# 2
yesterday = current_date - timedelta(days=1)
tomorrow = current_date + timedelta(days=1)
print(f"Yesterday: {yesterday}")
print(f"Today: {current_date}")
print(f"Tomorrow: {tomorrow}")


# 3
now = datetime.datetime.now()
now_without_microseconds = now.replace(microsecond=0)  # Efficient way
print(f"Now (with microseconds): {now}")
print(f"Now (without microseconds): {now_without_microseconds}")


# 4
date1 = datetime.datetime(2024, 1, 1, 10, 0, 0) # Example date and time
date2 = datetime.datetime(2024, 1, 1, 10, 0, 10) # Example date and time
time_difference = abs(date2 - date1) # Use abs to always get a positive difference
seconds_difference = time_difference.total_seconds()
print(f"Time difference between {date1} and {date2}: {seconds_difference} seconds")


# 5
date3 = datetime.date(2024, 1, 1)
date4 = datetime.date(2024, 1, 5)
date_difference = abs(date4 - date3)
days_difference = date_difference.days
print(f"Date difference between {date3} and {date4}: {days_difference} days")

# 6
date3_dt = datetime.datetime(date3.year, date3.month, date3.day) # Midnight of date3
date4_dt = datetime.datetime(date4.year, date4.month, date4.day) # Midnight of date4
date_difference_seconds = abs(date4_dt - date3_dt).total_seconds()
print(f"Date difference between {date3} and {date4} in seconds: {date_difference_seconds} seconds")