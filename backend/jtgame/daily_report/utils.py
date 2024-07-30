"""
Creation date: 2024/7/10
Creation Time: 下午5:04
DIR PATH: backend/jtgame/daily_report
Project Name: Manager_dvadmin
FILE NAME: untils.py
Editor: 30386
"""
import datetime
import re
from collections import defaultdict
from decimal import Decimal

import requests
from volcenginesdkcore import Configuration
from volcenginesdkcore.rest import ApiException
from volcenginesdkecs import ECSApi, DescribeInstancesRequest, RenewInstanceRequest

from dvadmin.utils.backends import logger
from jtgame.daily_report.models import ConsoleAccount, QuickAccount, Consoles
from jtgame.game_manage.models import Games


class ConsoleData:
    def make_daily_report(self, update=False):
        servers = []
        console_list = self.get_console_accounts()
        for console in console_list:
            self.set_configuration(console)
            ecs = self.get_ecs(console.account)
            servers.extend(ecs)
        if update:
            self.update_to_models(servers)
        return servers

    @staticmethod
    def update_to_models(instances):
        logs = []
        try:
            logs.append(f"获取实例信息: {len(instances)} 条")
            logs.append(f"原有实例信息: {Consoles.objects.count()} 条")
            Consoles.objects.all().delete()
            Consoles.objects.raw('ALTER TABLE jtgame_consoles AUTO_INCREMENT=1')
            for instance in instances:
                Consoles.objects.create(
                    account=instance['所属账号'],
                    instance_id=instance['实例ID'],
                    instance_name=instance['实例名称'],
                    status=instance['状态'],
                    instance_type_id=instance['规格'],
                    cpus=instance['CPU'],
                    memory_size=instance['内存'],
                    eip_address=instance['主IPv4地址'],
                    primary_ip_address=instance['次IPv4地址'],
                    instance_charge_type=instance['实例计费类型'],
                    expired_at=instance['到期时间']
                )
                logs.append(f"创建实例: {instance['实例名称']}")
            logs.append(f"更新实例信息: {Consoles.objects.count()} 条")
        except Exception as e:
            logs.append(f"更新实例信息失败: {str(e)}")
        return logs

    @staticmethod
    def get_console_accounts():
        return ConsoleAccount.objects.all()

    @staticmethod
    def set_configuration(console):
        configuration = Configuration()
        configuration.ak = console.access_key
        configuration.sk = console.secret_key
        configuration.region = "cn-shanghai"
        Configuration.set_default(configuration)

    def get_ecs(self, account, next_token=''):
        api_instance = ECSApi()
        describe_instances_request = DescribeInstancesRequest(max_results=100, next_token=next_token)
        try:
            api_result = api_instance.describe_instances(describe_instances_request)
            ecs_info = self.analysis_ecs(api_result.instances, account)
            next_token = api_result.next_token
            if next_token:
                ecs_info += self.get_ecs(account, next_token)
            return ecs_info
        except ApiException as e:
            logger.error(f"Exception when calling ECSApi: {e}")
            return []

    @staticmethod
    def analysis_ecs(instances, account):
        instance_infos = []
        for instance in instances:
            instance_dict = instance.to_dict()
            instance_infos.append({
                '实例ID': instance_dict['instance_id'],
                '实例名称': instance_dict['instance_name'],
                '状态': instance_dict['status'],
                '规格': instance_dict['instance_type_id'],
                'CPU': str(instance_dict['cpus']) + '核',
                '内存': str(int(instance_dict['memory_size']) / 1024) + 'GB',
                '主IPv4地址': instance_dict['eip_address']['ip_address'],
                '次IPv4地址': instance_dict['network_interfaces'][0]['primary_ip_address'],
                '实例计费类型': {'PostPaid': '按量计费', 'PrePaid': '包年包月'}.get(
                    instance_dict['instance_charge_type']
                ),
                '到期时间': datetime.datetime.strptime(
                    instance_dict['expired_at'], "%Y-%m-%dT%H:%M:%S+08:00"
                ).strftime("%Y-%m-%d %H:%M:%S") if instance_dict.get('expired_at') else '/',
                '所属账号': account
            })
        return instance_infos


class QuickTotal:
    def __init__(self, shifting_days=0):
        self.host_url = 'http://127.0.0.1:5010'
        self.shifting_days = shifting_days

    def make_daily_report(self):
        quick_datas = []
        bh_datas = self._initialize_bh_datas()
        quick_accounts = self.get_quick_accounts()

        for account in quick_accounts:
            try:
                quick_datas.extend(self.get_daily_reporter(account))
            except Exception as e:
                logger.error(f"Error processing account {account}: {e}")

        bh_datas = self._aggregate_data(quick_datas, bh_datas)
        banhao_datas = self._format_banhao_data(bh_datas)

        return quick_datas, banhao_datas

    @staticmethod
    def get_quick_accounts():
        return QuickAccount.objects.all()

    def get_daily_reporter(self, account):
        try:
            today = datetime.date.today()

            datas = self.get_income_details(account)
            yesterday_income = datas.get('yesterday_income', [])
            last_week_income = datas.get('last_week_income', [])
            last_month_income = datas.get('last_month_income', [])
            current_month_income = datas.get('current_month_income', [])

            merged_data = self._merge_game_data(yesterday_income, last_week_income, last_month_income,
                                                current_month_income)
            self._add_game_info(merged_data, today)
            logger.info(f'日报获取成功, 共 {len(merged_data)} 条')
            return merged_data
        except Exception as e:
            logger.error(f"Error getting daily report: {e}")
            return []

    def get_income_details(self, account) -> dict:
        try:
            result = requests.post(
                f'{self.host_url}/total',
                json={'account': account.account, 'password': account.password, 'shifting_days': self.shifting_days},
                timeout=300
            )
            if result.status_code == 200:
                return result.json()
            else:
                logger.error(f"Error getting income details: {result.text}")
                return {}
        except Exception as e:
            logger.error(f"Error getting income details: {e}")
            return {}

    @staticmethod
    def _initialize_bh_datas():
        return defaultdict(lambda: {
            '前一日充值': 0.0,
            '前七日内充值': 0.0,
            '前三十日内充值': 0.0,
            '上月总充值': 0.0,
            '昨日活跃用户（人）': 0.0
        })

    @staticmethod
    def _aggregate_data(quick_datas, bh_datas):
        try:
            for quick_data in quick_datas:
                game_name = quick_data['游戏名称'].split('（')[0]
                for key in ['前一日充值', '前七日内充值', '前三十日内充值', '上月总充值', '昨日活跃用户（人）']:
                    quick_data[key] = float(quick_data[key])
                    bh_datas[game_name][key] += quick_data[key]
            return {k: {sub_k: round(sub_v, 2) for sub_k, sub_v in v.items()} for k, v in bh_datas.items()}
        except Exception as e:
            logger.error(f"Error aggregating data: {e}")
            return bh_datas

    @staticmethod
    def _format_banhao_data(bh_datas):
        try:
            return [{'版号': k, '前一日总充值': v['前一日充值'], '前七日内总充值': v['前七日内充值'],
                     '前三十日内总充值': v['前三十日内充值'], '上月总充值': v['上月总充值'],
                     '昨日活跃总用户（人）': v['昨日活跃用户（人）']}
                    for k, v in bh_datas.items()]
        except Exception as e:
            logger.error(f"Error formatting banhao data: {e}")
            return []

    @staticmethod
    def search_game_by_quick_gamename(quick_gamename) -> Games:
        game = Games.objects.filter(quick_name=quick_gamename).first()
        return game if game else None

    @staticmethod
    def _merge_game_data(daily_data, weekly_data, monthly_data, current_month_data):
        try:
            merged_data = {}

            for data in daily_data:
                game_name = data["游戏名称"]
                merged_data[game_name] = {
                    "游戏名称": game_name,
                    "前一日充值": data.get("累计充值（元）", '0'),
                    "前七日内充值": '0',
                    "前三十日内充值": '0',
                    "上月总充值": '0',
                    "昨日活跃用户（人）": data.get("昨日活跃用户（人）", '')
                }

            for data in weekly_data:
                game_name = data["游戏名称"]
                if game_name in merged_data:
                    merged_data[game_name]["前七日内充值"] = data.get("累计充值（元）", '0')
                else:
                    merged_data[game_name] = {
                        "游戏名称": game_name,
                        "前一日充值": '0',
                        "前七日内充值": data.get("累计充值（元）", '0'),
                        "前三十日内充值": '0',
                        "上月总充值": '0',
                        "昨日活跃用户（人）": data.get("昨日活跃用户（人）", '')
                    }

            for data in monthly_data:
                game_name = data["游戏名称"]
                if game_name in merged_data:
                    merged_data[game_name]["前三十日内充值"] = data.get("累计充值（元）", '0')
                else:
                    merged_data[game_name] = {
                        "游戏名称": game_name,
                        "前一日充值": '0',
                        "前七日内充值": '0',
                        "前三十日内充值": data.get("累计充值（元）", '0'),
                        "上月总充值": '0',
                        "昨日活跃用户（人）": data.get("昨日活跃用户（人）", '')
                    }

            for data in current_month_data:
                game_name = data["游戏名称"]
                if game_name in merged_data:
                    merged_data[game_name]["上月总充值"] = data.get("累计充值（元）", '0')
                else:
                    merged_data[game_name] = {
                        "游戏名称": game_name,
                        "前一日充值": '0',
                        "前七日内充值": '0',
                        "前三十日内充值": '0',
                        "上月总充值": data.get("累计充值（元）", '0'),
                        "昨日活跃用户（人）": data.get("昨日活跃用户（人）", '')
                    }
            return list(merged_data.values())
        except Exception as e:
            logger.error(f"Error merging game data: {e}")
            return []

    def _add_game_info(self, merged_data, today):
        try:
            for data in merged_data:
                game_info = self.search_game_by_quick_gamename(data['游戏名称'])
                if game_info:
                    launch_days = (today - game_info.release_date).days
                    data['上线天数'] = launch_days
                    data['游戏名称'] = game_info.name
                    data['前一日充值'] = Decimal(data['前一日充值']) * game_info.reconciliation_ratio
                    data['前七日内充值'] = Decimal(data['前七日内充值']) * game_info.reconciliation_ratio
                    data['前三十日内充值'] = Decimal(data['前三十日内充值']) * game_info.reconciliation_ratio
                    data['上月总充值'] = Decimal(data['上月总充值']) * game_info.reconciliation_ratio
                else:
                    data['上线天数'] = '未知'
                    data['游戏名称'] = re.sub(r'0(?=\d)', '0.', data['游戏名称'], count=1)
        except Exception as e:
            logger.error(f"Error adding game info: {e}")


def RenewConsole(account: ConsoleAccount, instance_id: str):
    configuration = Configuration()
    configuration.ak = account.access_key
    configuration.sk = account.secret_key
    configuration.region = "cn-shanghai"
    # set default configuration
    Configuration.set_default(configuration)

    # use global default configuration
    api_instance = ECSApi()
    renew_instance_request = RenewInstanceRequest(
        instance_id=instance_id,
        period=1,
        period_unit="Month",
    )

    try:
        # 复制代码运行示例，请自行打印API返回值。
        result = api_instance.renew_instance(renew_instance_request)
        return {'status': True, 'message': '续费成功', 'data': result.to_dict()}
    except ApiException as e:
        return {'status': False, 'message': '续费失败', 'data': str(e)}
