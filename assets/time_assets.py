import datetime


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

