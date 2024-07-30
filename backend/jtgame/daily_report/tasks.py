"""
Creation date: 2024/7/18
Creation Time: 上午11:09
DIR PATH: backend/jtgame/daily_report
Project Name: Manager_dvadmin
FILE NAME: tasks.py
Editor: 30386
"""
import datetime
import json

from application.celery import app
from jtgame.daily_report.models import ReportData
from jtgame.daily_report.utils import ConsoleData, QuickTotal


@app.task
def task__make_daily_report(shifting_days=0):
    instances = ConsoleData().make_daily_report()
    income = QuickTotal(shifting_days).make_daily_report()

    data = {
        "instance": instances,
        "income": income[0],
        "banhao": income[1]
    }
    data = json.loads(json.dumps(data, ensure_ascii=False))
    today = datetime.date.today() - datetime.timedelta(days=shifting_days)
    today_str = today.strftime('%Y-%m-%d')
    try:
        report = ReportData.objects.filter(date=today).first()
        if report:
            report.data = data
            report.save()
            result = {"success": True, "status": "update", "error": "", "date": today_str}
        else:
            ReportData.objects.create(date=today, data=data)
            result = {"success": True, "status": "create", "error": "", "date": today_str}
    except Exception as e:
        result = {"success": False, "status": "error", "error": str(e), "date": today_str}

    return json.dumps(result, ensure_ascii=False)


@app.task
def task__update_consoles():
    try:
        ConsoleData().make_daily_report(update=True)
        return {"success": True, "status": "update", "error": ""}
    except Exception as e:
        return {"success": False, "status": "error", "error": str(e)}
