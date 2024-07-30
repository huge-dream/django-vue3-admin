"""
Creation date: 2024/7/2
Creation Time: 下午1:21
DIR PATH: backend/dvadmin/game_manage
Project Name: Manager_dvadmin
FILE NAME: untils.py
Editor: 30386
"""
import datetime
import json
import re

from django.db.models import Model

from jtgame.game_manage.models import Channel, Research, ResearchSplit, Games, RevenueSplit


def search_func(model: [Channel | Research], search_term) -> dict[str, [bool, str, Model]]:
    """
    查询函数
    :param model:
    :param search_term:
    :return:
    """
    models = [model for model in model.objects.all() if model.alias_contains(search_term)]

    if not models:
        error = f"{model}不存在: {search_term}"
        return {"status": False, "msg": error, "data": None}
    return {"status": True, "msg": "查询成功", "data": models[0]}


def search_channel(search_term):
    """
    查询渠道
    :param search_term:
    :return:
    """
    return search_func(Channel, search_term)


def search_research(search_term):
    """
    查询研发
    :param search_term:
    :return:
    """
    return search_func(Research, search_term)


def parse_request_data(request):
    data_bytes = request.body
    data_str = data_bytes.decode('utf-8').replace('\xae', '')
    return json.loads(data_str)


def get_discount_from_gamename(game_name: str) -> int:
    """
    从游戏名中获取折扣
    :param game_name:
    :return:
    """
    discount = 1
    if "折" in game_name and "0." in game_name:
        process = re.compile(r"0\.\d+")
        discount = int(1 / (float(process.findall(game_name)[0]) / 10))
    return discount


def handle_game(sheet, messages):
    table_data = sheet.get('tableData')
    game_name = sheet.get('gameName')
    release_date = sheet.get('releaseDate')
    parent = sheet.get('parent') or '靖堂'
    scheduling = sheet.get('scheduling')

    if not scheduling:
        release_date = datetime.datetime.strptime(release_date, '%Y-%m-%d').date()
        game, created = Games.objects.get_or_create(
            name=game_name,
            defaults={
                'release_date': release_date,
                'parent': parent,
                'status': int(datetime.datetime.now().date() >= release_date) + 1
            }
        )

        if created:
            msg = f'创建游戏: {game_name}'
            messages['info'].append(msg)
            # logger.info(msg)
        else:
            if game.status in [0, 1]:
                game.status = int(datetime.datetime.now().date() >= game.release_date) + 1
            game.parent = parent
            game.release_date = release_date
            game.save()
            msg = f'游戏已存在: {game_name}, 更新游戏状态为{game.get_status_display()}, 发行主体为{parent}, 发行时间为{release_date}'
            # print(msg)
            messages['update'].append(msg)
            # logger.info(msg)

        for data in table_data:
            process_channel_data(data, game, messages)

        return True
    return False


def process_channel_data(data, game, messages):
    load_in = False
    channel_name = ''

    for key, value in data.items():
        if '渠道名称' in key:
            channel_name = value.strip()
        elif '参数' in key:
            if value.strip():
                load_in = True

    if not load_in:
        return

    if not channel_name:
        msg = f'渠道名称为空: {game.name}'
        if msg not in messages['error']:
            messages['error'].append(msg)
            # logger.error(msg)
        return
    if channel_name == "渠道名称":
        return
    result = search_channel(channel_name)
    if not result.get('status'):
        msg = result.get('msg')
        if msg not in messages['error']:
            messages['error'].append(msg)
            # logger.error(msg)
        return

    channel: Channel = result.get('data')
    revenuesplit, update = RevenueSplit.objects.update_or_create(
        game=game,
        channel=channel,
        defaults={
            'our_ratio': channel.our_ratio,
            'channel_ratio': channel.channel_ratio,
            'channel_fee_ratio': channel.channel_fee_ratio,
            'channel_tips': channel.channel_tips
        }
    )
    if update:
        msg = f'创建游戏渠道分成: {game.name} - {channel_name}'
        messages['info'].append(msg)
        # logger.info(msg)
    else:
        msg = f'游戏渠道分成已存在: {game.name} - {channel_name}'
        messages['info'].append(msg)
        # logger.info(msg)


def handle_scheduling(sheet, messages):
    table_data = sheet.get('tableData')
    scheduling = sheet.get('scheduling')

    if scheduling:
        for data in table_data:
            game_name, research_name, quick, issue, _type = '', '', '', '', ''
            for key, value in data.items():
                if '游戏名称' in key:
                    game_name = value
                elif '研发公司' in key:
                    research_name = value
                elif 'quick后台名称' in key.lower():
                    quick = value
                elif '混服形式' in key:
                    issue = value
                elif '提测版本' in key:
                    _type = value

            if game_name and research_name:
                try:
                    game = Games.objects.filter(name=game_name).first()
                    if not game:
                        raise Games.DoesNotExist
                    if not quick.strip():
                        quick = game_name.replace(".", "")
                    game.quick_name = quick
                    game.issue = issue
                    game.type = _type
                    game.discount = get_discount_from_gamename(game_name)
                    game.save()
                    msg = (f'更新游戏: {game_name} - {quick} - '
                           f'{game.issue} - '
                           f'{game.type} - '
                           f'{game.discount}')
                    messages['update'].append(msg)
                except Games.DoesNotExist:
                    msg = f'游戏不存在: {game_name}'
                    if msg not in messages['error']:
                        messages['error'].append(msg)
                        # logger.error(msg)
                    continue

                result = search_research(research_name)
                if not result.get('status'):
                    msg = result.get('msg')
                    if msg not in messages['error']:
                        messages['error'].append(msg)
                        # logger.error(msg)
                    continue

                research: Research = result.get('data')
                reserchsplit, update = ResearchSplit.objects.update_or_create(
                    game=game,
                    research=research,
                    defaults={
                        'research_ratio': research.research_ratio,
                        'slotting_ratio': research.slotting_ratio,
                        'research_tips': research.research_tips,
                    }
                )
                if update:
                    msg = f'创建游戏研发分成: {game_name} - {research.name}'
                    messages['info'].append(msg)
                    # logger.info(msg)
                else:
                    msg = f'游戏研发分成已存在: {game_name} - {research.name}'
                    messages['info'].append(msg)
                    # logger.info(msg)
        return True
    return False


def get_last2word_from_channels():
    channels = []
    [channels.extend(_) for _ in Channel.objects.filter(status=True).values_list('alias', flat=True)]
    word2channel = [name[-2:].upper() for name in channels if
                    (len(name) > 2 and re.match(r'^[A-Z]{2}$', name[-2:].upper()))]
    word2channel = list(set(word2channel))
    return word2channel
