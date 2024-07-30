"""
Creation date: 2024/7/23
Creation Time: 上午11:18
DIR PATH: backend/jtgame/income_statement
Project Name: Manager_dvadmin
FILE NAME: tasks.py
Editor: 30386
"""
import json
import datetime

from application.celery import app
from jtgame.income_statement.models import IncomeData
from jtgame.income_statement.utils import QuickDetail


@app.task
def task__make_daily_detail_report(shifting_days=0):
    data, message = QuickDetail().make_daily_report()
    data = json.loads(json.dumps(data, ensure_ascii=False))
    message = json.loads(json.dumps(message, ensure_ascii=False))
    today = datetime.date.today() - datetime.timedelta(days=shifting_days)
    today_str = today.strftime('%Y-%m-%d')
    try:
        report = IncomeData.objects.filter(date=today).first()
        if report:
            report.data = data
            report.error = message
            report.save()
            result = {"success": True, "status": "update", "error": "", "date": today_str}
        else:
            IncomeData.objects.create(date=today, data=data, error=message)
            result = {"success": True, "status": "create", "error": "", "date": today_str}
    except Exception as e:
        result = {"success": False, "status": "error", "error": str(e), "date": today_str}

    return json.dumps(result, ensure_ascii=False)
