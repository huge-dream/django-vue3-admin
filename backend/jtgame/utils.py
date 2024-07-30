"""
Creation date: 2024/7/15
Creation Time: 下午4:49
DIR PATH: backend/jtgame
Project Name: Manager_dvadmin
FILE NAME: until.py
Editor: 30386
"""
from datetime import datetime, timedelta

import pytz


def parse_time_string(time_string: str) -> timedelta:
    """
    将时间字符串转换为 timedelta 对象。

    参数：
    time_string (str): 时间字符串，格式为 "HH:MM"。

    返回：
    timedelta: 表示时间的 timedelta 对象。

    异常：
    ValueError: 如果时间字符串格式不正确。
    """
    try:
        hours, minutes = map(int, time_string.split(':'))
        return timedelta(hours=hours, minutes=minutes)
    except ValueError:
        raise ValueError(f"无效的时间格式: {time_string}")


def parse_iso_datetime(date_string: str) -> datetime:
    """
    将ISO 8601格式的日期字符串转换为 datetime 对象。

    参数：
    date_string (str): ISO 8601格式的日期字符串。

    返回：
    datetime: 表示日期时间的 datetime 对象。

    异常：
    ValueError: 如果日期字符串格式不正确。
    """
    try:
        if date_string.endswith('Z'):
            utc_dt = datetime.fromisoformat(date_string.replace("Z", "+00:00")).replace(second=0, microsecond=0)
        elif '+' in date_string or '-' in date_string:
            utc_dt = datetime.fromisoformat(date_string).replace(second=0, microsecond=0)
        else:
            utc_dt = datetime.fromisoformat(date_string + "+00:00").replace(second=0, microsecond=0)
        local_tz = pytz.timezone('Asia/Shanghai')
        local_dt = utc_dt.astimezone(local_tz)
        local_tz_dt = local_dt.replace(tzinfo=None)
        return local_tz_dt
    except ValueError:
        raise ValueError(f"无效的日期格式: {date_string}")
