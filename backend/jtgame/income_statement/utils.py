"""
Creation date: 2024/7/19
Creation Time: 下午3:00
DIR PATH: backend/jtgame/income_statement
Project Name: Manager_dvadmin
FILE NAME: utils.py
Editor: 30386
"""
import re
from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from decimal import Decimal

import requests
from django.db.models import QuerySet

from dvadmin.utils.backends import logger
from jtgame.daily_report.models import QuickAccount
from jtgame.game_manage.models import Games, ResearchSplit, RevenueSplit, Channel
from jtgame.game_manage.utils import get_last2word_from_channels, search_func


class QuickDetail:
    def __init__(self, shifting_days: int = 0):
        self.host_url = 'http://127.0.0.1:5010'
        self.shifting_days = shifting_days
        self.dis_words = get_last2word_from_channels()

        self.game_temp = {}
        self.channel_temp = {}
        self.revenue_split_temp = {}
        self.research_split_temp = {}

        self.games: QuerySet = Games.objects.all()
        self.research_splits: QuerySet = ResearchSplit.objects.select_related(
            'game', 'research').all()
        self.revenue_splits: QuerySet = RevenueSplit.objects.select_related(
            'game', 'channel').all()

    def make_daily_report(self):
        stime = datetime.now()
        quick_datas = []
        message = {'info': [], 'error': [], 'warning': []}

        quick_accounts = self.get_quick_accounts()
        for account in quick_accounts:
            try:
                quick_datas.append(self.get_daily_reporter(account, message))
            except Exception as e:
                logger.error(f"Error processing account {account}: {e}")

        merge_datas = self._merge_data(quick_datas)

        self._merge_message(message)
        etime = datetime.now()
        self._add_message(message, 'info', f"日报生成完成, 共耗时: {etime - stime}")

        return merge_datas, message

    @staticmethod
    def _merge_message(message) -> None:
        game_warning_count = 0
        channel_warning_count = 0
        revenue_split_warning_count = 0
        research_split_warning_count = 0

        for warning in message['warning']:
            if "未找到游戏信息" in warning:
                game_warning_count += 1
            elif "未找到渠道信息" in warning:
                channel_warning_count += 1
            elif "未找到渠道分成信息" in warning:
                revenue_split_warning_count += 1
            elif "未找到研发分成信息" in warning:
                research_split_warning_count += 1

        message['info'].append(f"共有 {game_warning_count} 条未查到游戏信息")
        message['info'].append(f"共有 {channel_warning_count} 条未查到渠道信息")
        message['info'].append(f"共有 {revenue_split_warning_count} 条未查到渠道分成信息")
        message['info'].append(f"共有 {research_split_warning_count} 条未查到研发分成信息")

        message['info'].append(f"共有 {len(message['error'])} 条错误信息")
        message['info'].append(f"共有 {len(message['warning'])} 条警告信息")

    @staticmethod
    def _merge_data(quick_datas):
        idx = 0
        merged_datas = {}
        for quick_data in quick_datas:
            for key in quick_data.keys():
                if key not in merged_datas:
                    merged_datas[key] = []
                for quick_item in quick_data[key]:
                    quick_item['id'] = idx
                    idx += 1
                    for child in quick_item['children']:
                        child['id'] = idx
                        idx += 1
                merged_datas[key].extend(quick_data[key])
        return merged_datas

    @staticmethod
    def get_quick_accounts() -> QuerySet:
        return QuickAccount.objects.all()

    def get_daily_reporter(self, account: QuickAccount, message):
        filled_datas = {}
        try:
            datas = self.get_income_details(account, message)
            filled_datas = {key: self._fill_data(datas.get(key, []), message) for key in
                            ['current_month_income', 'this_month_income', 'last_month_income',
                             'last_week_income', 'yesterday_income']}
        except Exception as e:
            msg = f"获取日报失败: {e}"
            logger.error(msg)
            message['error'].append(msg)

        return filled_datas

    def get_income_details(self, account: QuickAccount, message):
        try:
            result = requests.post(
                f'{self.host_url}/detail',
                json={'account': account.account, 'password': account.password, 'shifting_days': self.shifting_days},
                timeout=300
            )
            if result.status_code == 200:
                return result.json()
            else:
                msg = f"访问收入详情接口失败: {result.text}"
                logger.error(msg)
                message['error'].append(msg)
                return {}
        except Exception as e:
            msg = f"获取收入详情失败: {e}"
            logger.error(msg)
            message['error'].append(msg)
            return {}

    def search_game_by_quick_gamename(self, quick_gamename: str) -> Games:
        game = self.games.filter(quick_name=quick_gamename).first()
        return game if game else None

    @staticmethod
    def search_channel_by_alias(alias: str) -> Channel:
        return search_func(Channel, alias)['data']

    def use_game_temp(self, game: str) -> Games:
        return self.game_temp.get(game, self.check_game(game))

    def check_game(self, game: str) -> Games:
        result = self.search_game_by_quick_gamename(game)
        self.game_temp[game] = result
        return result

    def use_channel_temp(self, channel: str):
        return self.channel_temp.get(channel, self.check_channel(channel))

    def check_channel(self, channel: str):
        result = len(channel) > 1 and re.match('^[A-z]{2}$', channel[-2:]) and not any(
            channel.endswith(_) for _ in self.dis_words)
        channel_obj = self.search_channel_by_alias(channel if not result else channel[:-2])
        self.channel_temp[channel] = result, channel_obj
        return result, channel_obj

    def use_revenue_split_temp(self, channel: str, game: str) -> RevenueSplit:
        return self.revenue_split_temp.get(f"{channel}-{game}", self.check_revenue_split(channel, game))

    def check_revenue_split(self, channel: str, game: str) -> RevenueSplit:
        revenue_split = self.revenue_splits.filter(game=game, channel=channel).first()
        self.revenue_split_temp[f"{channel}-{game}"] = revenue_split if revenue_split else None
        return revenue_split

    def use_research_split_temp(self, game: str) -> ResearchSplit:
        return self.research_split_temp.get(game, self.check_research_split(game))

    def check_research_split(self, game: str) -> ResearchSplit:
        research_split = self.research_splits.filter(game=game).first()
        self.research_split_temp[game] = research_split if research_split else None
        return research_split

    def _fill_data(self, data, message) -> list[dict[str, any]]:
        game_data = defaultdict(lambda: {
            "game": "",
            "main_body": "",
            "release_date": "",
            "discount": "",
            "research_name": "",
            "research_company": "",
            "slotting_ratio": "",
            "research_ratio": "",
            "research_tips": "",
            "reconciliation_ratio": "",
            "children": [],
            "channel": "",
            "recharge": Decimal(0),
            "our_ratio": "",
            "our_income": Decimal(0),
            "channel_fee": "",
            "channel_tips": "",
            "after_folding": Decimal(0),
            "channel_company": "",
            "research_income": Decimal(0),
            "our_folding_income": Decimal(0),
            "research_folding_income": Decimal(0)
        })
        for item in data:
            try:
                self._process_item(item, message)
                game_key = item['game']
                channel_data = deepcopy(item)
                for key in ['game', 'main_body', 'release_date', 'discount', 'research_name', 'research_company',
                            'slotting_ratio', 'research_ratio', 'research_tips']:
                    if key in channel_data:
                        if not game_data[game_key][key]:
                            game_data[game_key][key] = channel_data[key]
                        if key == 'game':
                            channel_data[key] = ""
                    else:
                        channel_data[key] = f"信息缺失"
                for key in ['recharge', 'our_income', 'after_folding', 'research_income', 'our_folding_income',
                            'research_folding_income']:
                    if key in channel_data:
                        game_data[game_key][key] += Decimal(channel_data[key])
                    else:
                        channel_data[key] = 0
                for key, value in channel_data.items():
                    channel_data[key] = str(value)
                game_data[game_key]['children'].append(channel_data)
            except Exception as e:
                msg = f"处理匹配数据失败: {e}"
                logger.error(msg)
                message['error'].append(msg)

        for key, value in game_data.items():
            for _key, _value in value.items():
                if _key != 'children':
                    value[_key] = str(_value)
            if value['children']:
                game_data[key]['channel'] = f"{len(value['children'])}个渠道"

        return list(game_data.values())

    def _process_item(self, item, message) -> bool:
        channel = item.get('channel')
        result, channel_obj = self.use_channel_temp(channel)
        if result:
            item['game'] += channel[-2:]

        if not channel_obj:
            self._add_message(message, 'warning', f"*[{item['channel']}: {item['game']}] 未找到渠道信息, 请检查")
            return False
        item['channel'] = str(channel_obj.name)

        game_obj = self.use_game_temp(item['game'])
        if not game_obj:
            self._add_message(message, 'warning', f"*[{item['channel']}: {item['game']}] 未找到游戏信息, 请检查")
            return False
        item['game'] = str(game_obj.name)

        revenue_split_obj = self.use_revenue_split_temp(channel_obj.id, game_obj.id)
        if not revenue_split_obj:
            self._add_message(message, 'warning', f"*[{item['channel']}: {item['game']}] 未找到渠道分成信息, 请检查")
            return False

        research_split_obj = self.use_research_split_temp(game_obj.id)
        if not research_split_obj:
            self._add_message(message, 'warning', f"*[{item['channel']}: {item['game']}] 未找到研发分成信息, 请检查")
            return False

        self._calculate_financials(item, game_obj, channel_obj, revenue_split_obj, research_split_obj)
        # for key, value in item.items():
        #     item[key] = str(value)
        # print(
        #     f"处理数据: {item['game']} - "
        #     f"{item['channel']} - {item['recharge']} - "
        #     f"{item['our_income']} - {item['research_income']}")
        return True

    def _calculate_financials(self, item, game_obj: Games, channel_obj: Channel,
                              revenue_split_obj: RevenueSplit, research_split_obj: ResearchSplit) -> None:
        item['recharge'] = Decimal(item['recharge'])
        item['main_body'] = str(game_obj.parent)
        item['release_date'] = str(game_obj.release_date)
        item['discount'] = game_obj.discount
        item['reconciliation_ratio'] = game_obj.reconciliation_ratio
        item['channel_company'] = str(channel_obj.company_name)
        item['research_name'] = str(research_split_obj.research.name)
        item['research_company'] = str(research_split_obj.research.company_name)
        item['after_folding'] = Decimal(item['recharge'] / game_obj.discount)
        item['channel_fee'] = f"{revenue_split_obj.channel_fee_ratio / 100}"
        item['our_ratio'] = f"{revenue_split_obj.our_ratio / 100}"
        item['slotting_ratio'] = f"{research_split_obj.slotting_ratio / 100}"
        item['research_ratio'] = f"{research_split_obj.research_ratio / 100}"
        item['our_income'] = self._calculate_income(
            item['recharge'], revenue_split_obj.our_ratio, revenue_split_obj.channel_fee_ratio)
        item['our_folding_income'] = self._calculate_income(
            item['after_folding'], revenue_split_obj.our_ratio, revenue_split_obj.channel_fee_ratio)
        item['research_income'] = self._calculate_income(
            item['recharge'], research_split_obj.research_ratio, research_split_obj.slotting_ratio)
        item['research_folding_income'] = self._calculate_income(
            item['after_folding'], research_split_obj.research_ratio, research_split_obj.slotting_ratio)
        item['channel_tips'] = str(revenue_split_obj.channel_tips)
        item['research_tips'] = str(research_split_obj.research_tips)

    @staticmethod
    def _calculate_income(amount: Decimal, ratio: Decimal, fee: Decimal) -> Decimal:
        return Decimal(amount * (ratio / 100) * (1 - fee / 100))

    @staticmethod
    def _add_message(message, level: str, text: str) -> None:
        if text not in message[level]:
            message[level].append(text)
