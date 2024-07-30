from django.core.exceptions import ValidationError
from django.db import models

from dvadmin.system.models import Dept
from dvadmin.utils.models import CoreModel, table_prefix


# Create your models here.


class Channel(CoreModel):
    CHANNEL_STATUS = ((0, '禁用'), (1, '启用'))

    # 渠道名称
    name = models.CharField(max_length=100, verbose_name='渠道名称')
    # 渠道别名(列表)
    alias = models.JSONField(verbose_name='渠道别名', null=True, blank=True)
    # 渠道公司名
    company_name = models.CharField(max_length=100, verbose_name='渠道公司名')
    # 我方分成比例
    our_ratio = models.DecimalField(verbose_name='我方分成比例', default=30, max_digits=5, decimal_places=0)
    # 渠道分成比例
    channel_ratio = models.DecimalField(verbose_name='渠道分成比例', default=70, max_digits=5, decimal_places=0)
    # 渠道费比例
    channel_fee_ratio = models.DecimalField(verbose_name='渠道费比例', default=5, max_digits=5, decimal_places=0)
    # 渠道备注
    channel_tips = models.TextField(verbose_name='渠道备注', null=True, blank=True)
    # 渠道状态
    status = models.IntegerField(choices=CHANNEL_STATUS, default=1, verbose_name='渠道状态')

    class Meta:
        db_table = table_prefix + 'game_manage_channel'
        verbose_name = '渠道管理'
        verbose_name_plural = verbose_name
        ordering = ("name",)

    def clean(self):
        super().clean()
        if self.alias:
            if not isinstance(self.alias, list):
                raise ValidationError("渠道别名必须是一个列表")
            for item in self.alias:
                if not isinstance(item, str):
                    raise ValidationError("渠道别名列表中的每个元素都必须是字符串")

    def __str__(self):
        return self.name

    def alias_contains(self, search_term):
        if not self.alias:
            return False
        if isinstance(self.alias, str):
            aliases = self.alias.split('、')
        elif isinstance(self.alias, list):
            aliases = self.alias
        else:
            return False
        for alias in aliases:
            if alias.upper() in search_term.upper():
                return True
        return False


# 研发
class Research(CoreModel):
    RESEARCH_STATUS = ((0, '禁用'), (1, '启用'))
    # 研发名称
    name = models.CharField(max_length=100, verbose_name='研发名称')
    # 研发别名
    alias = models.JSONField(verbose_name='研发别名', null=True, blank=True)
    # 研发公司名
    company_name = models.CharField(max_length=100, verbose_name='研发公司名')
    # 研发分成比例
    research_ratio = models.DecimalField(verbose_name='研发分成比例', default=15, max_digits=5, decimal_places=0)
    # 通道费比例
    slotting_ratio = models.DecimalField(verbose_name='通道费比例', default=0, max_digits=5, decimal_places=0)
    # 研发备注
    research_tips = models.TextField(verbose_name='研发备注', null=True, blank=True)
    # 研发状态
    status = models.IntegerField(choices=RESEARCH_STATUS, default=1, verbose_name='研发状态')

    class Meta:
        db_table = table_prefix + 'game_manage_research'
        verbose_name = '研发管理'
        verbose_name_plural = verbose_name
        ordering = ("name",)

    def clean(self):
        super().clean()
        if self.alias:
            if not isinstance(self.alias, list):
                raise ValidationError("研发别名必须是一个列表")
            for item in self.alias:
                if not isinstance(item, str):
                    raise ValidationError("研发别名列表中的每个元素都必须是字符串")

    def __str__(self):
        return self.name

    def alias_contains(self, search_term):
        if not self.alias:
            return False
        if isinstance(self.alias, str):
            aliases = self.alias.split('、')
        elif isinstance(self.alias, list):
            aliases = self.alias
        else:
            return False
        for alias in aliases:
            if alias.upper() in search_term.upper():
                return True
        return False


# 游戏
class Games(CoreModel):
    GAME_STATUS = ((0, '未知'), (1, '未上线'), (2, '已上线'), (3, '已下架'), (4, '已关服'))
    # 游戏名称
    name = models.CharField(max_length=100, verbose_name='游戏上线名称')
    # 游戏quick名称
    quick_name = models.CharField(max_length=100, verbose_name='游戏quick名称')
    # 游戏类型
    type = models.CharField(max_length=100, verbose_name='游戏类型', default='未知')
    # 游戏发行时间
    release_date = models.DateField(verbose_name='游戏发行时间', null=True, blank=True, default=None)
    # 游戏停新增时间
    stop_add_date = models.DateField(verbose_name='游戏停新增时间', null=True, blank=True, default=None)
    # 游戏停充值时间
    stop_recharge_date = models.DateField(verbose_name='游戏停充值时间', null=True, blank=True, default=None)
    # 游戏停运营时间
    stop_operation_date = models.DateField(verbose_name='游戏停运营时间', null=True, blank=True, default=None)
    # 游戏发行主体
    parent = models.CharField(max_length=100, verbose_name='游戏发行主体')
    # 游戏状态
    status = models.IntegerField(choices=GAME_STATUS, default=0, verbose_name='游戏状态')
    # 游戏发行类型
    issue = models.CharField(max_length=100, verbose_name='游戏发行类型', default='未知')
    # 游戏折扣
    discount = models.DecimalField(default=1, verbose_name='游戏折扣', max_digits=10, decimal_places=0)
    # 对账比例
    reconciliation_ratio = models.DecimalField(verbose_name='对账比例', default=1, max_digits=5, decimal_places=0)
    # 游戏描述
    desc = models.TextField(verbose_name='游戏描述', null=True, blank=True)

    class Meta:
        db_table = table_prefix + 'game_manage_games'
        verbose_name = '游戏管理'
        verbose_name_plural = verbose_name
        ordering = ("-release_date",)

    def __str__(self):
        return self.name


# 游戏渠道分成
class RevenueSplit(CoreModel):
    # 游戏名称
    game = models.ForeignKey(Games, verbose_name='游戏名称', on_delete=models.CASCADE)
    # 渠道名称
    channel = models.ForeignKey(Channel, verbose_name='渠道名称', on_delete=models.CASCADE)
    # 我方分成比例
    our_ratio = models.DecimalField(verbose_name='我方分成比例', max_digits=5, decimal_places=0)
    # 渠道分成比例
    channel_ratio = models.DecimalField(verbose_name='渠道分成比例', max_digits=5, decimal_places=0)
    # 渠道费比例
    channel_fee_ratio = models.DecimalField(verbose_name='渠道费比例', max_digits=5, decimal_places=0)
    # 渠道备注
    channel_tips = models.TextField(verbose_name='分成备注', null=True, blank=True)

    class Meta:
        db_table = table_prefix + 'game_manage_revenue_split'
        verbose_name = '游戏渠道分成'
        verbose_name_plural = verbose_name
        ordering = ("game", "channel")


# 游戏研发分成
class ResearchSplit(CoreModel):
    # 游戏名称
    game = models.ForeignKey(Games, verbose_name='游戏名称', on_delete=models.CASCADE)
    # 研发名称
    research = models.ForeignKey(Research, verbose_name='研发名称', on_delete=models.CASCADE)
    # 研发分成比例
    research_ratio = models.DecimalField(verbose_name='研发分成比例', max_digits=5, decimal_places=0)
    # 通道费比例
    slotting_ratio = models.DecimalField(verbose_name='通道费比例', max_digits=5, decimal_places=0)
    # 研发备注
    research_tips = models.TextField(verbose_name='分成备注', null=True, blank=True)

    class Meta:
        db_table = table_prefix + 'game_manage_research_split'
        verbose_name = '游戏研发分成'
        verbose_name_plural = verbose_name
        ordering = ("game", "research")
