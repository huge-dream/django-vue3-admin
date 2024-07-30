from datetime import datetime, timedelta
from typing import Tuple

import pytz

from dvadmin.utils.backends import logger
from jtgame.utils import parse_time_string


def calculate_work_hours(start: datetime, end: datetime,
                         work_start_morning: str, work_end_morning: str,
                         work_start_afternoon: str, work_end_afternoon: str) -> Tuple[int, int]:
    """
    计算在指定时间段内的工作时间（天数和小时数）。

    参数：
    start (str): 开始时间，ISO 8601格式的日期字符串。
    end (str): 结束时间，ISO 8601格式的日期字符串。
    work_start_morning (str): 上午工作开始时间，格式为 "HH:MM"。
    work_end_morning (str): 上午工作结束时间，格式为 "HH:MM"。
    work_start_afternoon (str): 下午工作开始时间，格式为 "HH:MM"。
    work_end_afternoon (str): 下午工作结束时间，格式为 "HH:MM"。

    返回：
    Tuple[int, int]: 返回一个元组，第一个元素是请假天数，第二个元素是请假小时数。

    异常：
    ValueError: 当时间段参数类型错误或逻辑错误时抛出。
    """
    # 将ISO 8601日期字符串转换为 datetime 对象
    logger.info(f'请假时间段：{start} - {end}')

    # 将时间字符串转换为 timedelta 对象
    work_start_morning = parse_time_string(work_start_morning)
    work_end_morning = parse_time_string(work_end_morning)
    work_start_afternoon = parse_time_string(work_start_afternoon)
    work_end_afternoon = parse_time_string(work_end_afternoon)

    # 初始化工作秒数为0
    work_seconds = 0

    # 参数验证
    if not all(isinstance(param, timedelta) for param in
               [work_start_morning, work_end_morning, work_start_afternoon, work_end_afternoon]):
        raise ValueError("工作时间段参数必须是 timedelta 类型")
    if start > end:
        raise ValueError("开始时间必须早于结束时间")
    if work_start_morning >= work_end_morning or work_start_afternoon >= work_end_afternoon:
        raise ValueError("上班时间段必须早于下班时间段")

    # 初始化当前时间为开始时间
    current = start
    while current < end:
        if current.weekday() >= 5:  # 如果是周末，跳到下一个工作日
            current += timedelta(days=1)
            current = current.replace(hour=work_start_morning.seconds // 3600,
                                      minute=(work_start_morning.seconds // 60) % 60, second=0, microsecond=0)
            continue

        # 定义当前工作日的开始和结束时间
        work_day_start = current.replace(hour=work_start_morning.seconds // 3600,
                                         minute=(work_start_morning.seconds // 60) % 60,
                                         second=0, microsecond=0)
        work_day_end = current.replace(hour=work_end_afternoon.seconds // 3600,
                                       minute=(work_end_afternoon.seconds // 60) % 60,
                                       second=0, microsecond=0)

        if current < work_day_start:  # 如果当前时间早于工作开始时间
            current = work_day_start  # 跳到工作开始时间

        # 处理上午工作时间段
        if work_day_start <= current < current.replace(hour=work_end_morning.seconds // 3600,
                                                       minute=(work_end_morning.seconds // 60) % 60):
            end_period = min(end, current.replace(hour=work_end_morning.seconds // 3600,
                                                  minute=(work_end_morning.seconds // 60) % 60))  # 计算上午工作结束时间
            work_seconds += (end_period - current).total_seconds()  # 计算并累计工作秒数
            current = end_period  # 更新当前时间

        # 处理中午休息时间，如果当前时间在午休时间段内，跳到下午工作开始时间
        if current.replace(hour=work_end_morning.seconds // 3600,
                           minute=(work_end_morning.seconds // 60) % 60) <= current < current.replace(
            hour=work_start_afternoon.seconds // 3600, minute=(work_start_afternoon.seconds // 60) % 60):
            current = current.replace(hour=work_start_afternoon.seconds // 3600,
                                      minute=(work_start_afternoon.seconds // 60) % 60, second=0, microsecond=0)

        # 处理下午工作时间段
        if work_day_start.replace(hour=work_start_afternoon.seconds // 3600,
                                  minute=(work_start_afternoon.seconds // 60) % 60) <= current < work_day_end:
            end_period = min(end, work_day_end)  # 计算下午工作结束时间
            work_seconds += (end_period - current).total_seconds()  # 计算并累计工作秒数
            current = end_period  # 更新当前时间

        if current >= work_day_end:  # 如果当前时间晚于工作结束时间，跳到下一工作日
            current += timedelta(days=1)
            current = current.replace(hour=work_start_morning.seconds // 3600,
                                      minute=(work_start_morning.seconds // 60) % 60, second=0, microsecond=0)

    # 将总秒数转换为小时，并向上取整
    work_hours = int((work_seconds + 3599) // 3600)
    leave_days = work_hours // 8
    leave_hours = work_hours % 8

    if leave_days < 0:
        raise ValueError("计算有误，请确保起始时间有效")

    return leave_days, leave_hours
