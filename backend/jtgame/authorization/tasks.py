"""
Creation date: 2024/7/18
Creation Time: 上午11:01
DIR PATH: backend/jtgame/authorization
Project Name: Manager_dvadmin
FILE NAME: tasks.py
Editor: 30386
"""
import json

import requests

from application.celery import app
from jtgame.authorization.models import AuthorizationConfig, AuthorizationInfo, AuthorizationLetter


@app.task
def generate_authorization_letter(obj_id):
    obj = AuthorizationLetter.objects.get(pk=obj_id)
    obj: AuthorizationLetter

    try:
        bh_name = obj.name
        su_name = ''
        if '（' in bh_name:
            bh_name = obj.name.split('（')[0]
            su_name = obj.name.split('（')[1].split('）')[0]

        authorization_obj = AuthorizationInfo.objects.filter(name=bh_name).first()
        if not authorization_obj:
            raise Exception('未找到对应的版号信息')
        authorization_obj: AuthorizationInfo

        config_objs = AuthorizationConfig.objects.all()
        if not config_objs:
            raise Exception('未找到授权书配置信息')

        dir_path = config_objs.filter(key='dir_path').first()
        if not dir_path:
            raise Exception('未找到授权书模板的路径配置')
        dir_path = json.loads(dir_path.value).get(authorization_obj.entity, None)
        if not dir_path:
            raise Exception('未找到对应主体的模板的存放路径')

        webhook_key = config_objs.filter(key='webhook_key').first()
        if not webhook_key:
            raise Exception('未找到发送通知的webhook_key配置')
        webhook_key = webhook_key.value

        data = {
            'webhook_key': str(webhook_key),
            'file_name': str(obj.name),
            'dir_path': str(dir_path),
            'replacement_dict': {
                '彡': str(obj.name),
                '亇': str(bh_name),
                '⺧': str(authorization_obj.publisher),
                '丷': str(authorization_obj.software_registration_number),
                '⺌': str(authorization_obj.isbn),
                '艹': str(authorization_obj.publication_approval_number),
                '冖': str(obj.release_date),
                '宀': str(authorization_obj.authorization_end_date),
                '亠': str(obj.release_date),
                '⻗': str(obj.release_date),
                '⺋': str(bh_name),
                '彐': str(su_name),
                '⺈': str(authorization_obj.icp_license)
            }
        }
        result = requests.post('http://localhost:5020/build', json=data).json()
        if result.get('error'):
            obj.tips = result.get('error')
            if result.get('zip_file'):
                obj.status = 4
                obj.authorization_filepath = result.get('zip_file')
                obj.tips = '生成成功, 但发送失败'
            else:
                obj.status = 3
        else:
            obj.authorization_filepath = result.get('zip_file')
            obj.tips = '生成成功'
            obj.status = 1
        obj.save()
    except Exception as e:
        obj.tips = str(e)
        obj.status = 3
        obj.save()
        raise e
