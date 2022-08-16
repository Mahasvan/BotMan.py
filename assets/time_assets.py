import datetime
import time


def get_time(time):
    if time is not None:
        if time[-1] == 'd':
            time_final = int(time[-1]) * 3600 * 24
        elif time[-1] == 'h':
            time_final = int(time[:-1]) * 3600
        elif time[-1] == 'm':
            time_final = int(time[:-1]) * 60
        elif time[-1] == 's':
            time_final = int(time[:-1])
        else:
            time_final = int(time)
        return time_final


def parse_utc(utc_str: str):
    date = utc_str[:10]
    time = utc_str[11:19]
    return date, time


def time_suffix(time):
    if time is not None:
        if time[-1] == 'd':
            final_thing = str(time)[:-1] + ' days'
        elif time[-1] == 'h':
            if not time[:-1] == '1':
                final_thing = str(time)[:-1] + ' hours'
            else:
                final_thing = str(time)[:-1] + ' hour'
        elif time[-1] == 'm':
            if not time[:-1] == '1':
                final_thing = str(time)[:-1] + ' minutes'
            else:
                final_thing = str(time)[:-1] + ' minute'
        elif time[-1] == 's':
            if time[:-1] == '1':
                final_thing = str(time)[:-1] + ' second'
            else:
                final_thing = str(time)[:-1] + ' seconds'
        else:
            if time == '1':
                final_thing = str(time) + ' second'
            else:
                final_thing = str(time) + ' seconds'
        return final_thing


def format_time(time: str):
    am_pm = "AM"
    time_hours = int(time[:2])
    time_minutes = int(time[3:])
    if time_hours >= 12:
        time_hours -= 12
        am_pm = "PM"
    if len(str(time_hours)) == 1:
        time_hours = f"0{time_hours}"
    if len(str(time_minutes)) == 1:
        time_minutes = f"0{time_minutes}"
    return f"{time_hours}:{time_minutes} {am_pm}"


def time_from_offset(timezone):
    now = str(datetime.datetime.utcnow())
    offset_hours, offset_minutes = timezone.split(":")
    if int(offset_hours) < 0:
        offset_minutes = int(offset_minutes) * -1
    time = now.split(" ")[1]
    hour, minute, second = time.split(':')
    hour = int(hour) + int(offset_hours)
    minute = int(minute) + int(offset_minutes)
    if minute >= 60:
        hour += 1
        minute -= 60
    if minute < 0:
        hour -= 1
        minute += 60
    return f"{hour}:{minute}"


def get_pretty_time_remaining_from_unix(unix_time, now_time=None):
    if not now_time:
        now_time = time.time()
    time_remaining = int(float(unix_time) - float(now_time))
    return get_pretty_time_remaining_from_unix(time_remaining)


def pretty_time_from_seconds(time_remaining: int):
    if time_remaining < 0:
        return "0 seconds"
    minutes, seconds = divmod(time_remaining, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)

    final_string_to_join = []
    if weeks > 0:
        final_string_to_join.append(f"{weeks} {'weeks' if weeks != 1 else 'week'}")
    if days > 0:
        final_string_to_join.append(f"{days} {'days' if days != 1 else 'day'}")
    if hours > 0:
        final_string_to_join.append(f"{hours} {'hours' if hours != 1 else 'hour'}")
    if minutes > 0:
        final_string_to_join.append(f"{minutes} {'minutes' if minutes != 1 else 'minute'}")
    if seconds > 0:
        final_string_to_join.append(f"{seconds} {'seconds' if seconds != 1 else 'second'}")

    if len(final_string_to_join) > 1:
        final_string = ", ".join(final_string_to_join[:-1]) + f", and {final_string_to_join[-1]}"
    else:
        final_string = ", ".join(final_string_to_join)
    return final_string


def get_seconds_from_input(input_time_str: str):
    """Thanks to CorpNewt for helping out with this function"""
    accepted_chars = {
        "w": 604_800,
        "d": 86_400,
        "h": 3_600,
        "m": 60,
        "s": 1
    }
    time_seconds = 0
    last_number = ""
    for char in input_time_str:
        if char.isdigit():  # Check if we have a number
            last_number += char
        elif char in accepted_chars:  # Check if it's a valid suffix, and we have a time so far
            if last_number == "":
                continue
            time_seconds += int(last_number) * accepted_chars[char]
            last_number = ""
        else:
            last_number = ""
    if last_number:  # Check if we have any left - and add it
        time_seconds += int(last_number)
    return time_seconds

def format_date_yyyymmdd(date, sep="-"):
    month_dict = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
    }

    items = date.split(sep)
    if not len(items) == 3:
        return date
    year, month, date = items
    month = month_dict.get(int(month), "Invalid")
    date = int(date)
    return f"{date} {month}, {year}"
