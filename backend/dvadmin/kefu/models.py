from django.db import models
from dvadmin.utils.models import CoreModel, table_prefix, get_custom_app_models


class Group(CoreModel):
    name = models.CharField(null=False, max_length=64, verbose_name="群组名称", help_text="群组名称")
    mark = models.CharField(max_length=32, verbose_name="群组说明", help_text="群组说明")

    class Meta:
        db_table = table_prefix + "group"
        verbose_name = "坐席群组表"
        verbose_name_plural = verbose_name


class SipUser(CoreModel):
    name = models.CharField(null=False, max_length=64, verbose_name="坐席名称", help_text="坐席名称")
    number = models.CharField(max_length=32, verbose_name="坐席号码", help_text="坐席号码")
    passwd = models.CharField(max_length=32, verbose_name="坐席密码", help_text="坐席密码")
    STATUS_CHOICES = (
        (0, "禁用"),
        (1, "启用"),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="坐席状态", help_text="坐席状态")
    REGISTERED_CHOICES = (
        (0, "未注册"),
        (1, "已注册"),
    )
    registered = models.IntegerField(choices=REGISTERED_CHOICES, default=1, verbose_name="注册状态", help_text="注册状态")

    group = models.ManyToManyField(to="Group", blank=True, verbose_name="关联群组", db_constraint=False,
                                   help_text="关联群组")

    class Meta:
        db_table = table_prefix + "sip_user"
        verbose_name = "坐席表"
        verbose_name_plural = verbose_name
        ordering = ("number",)


class SipTrunk(CoreModel):
    name = models.CharField(null=False, max_length=64, verbose_name="通道名称", help_text="通道名称")
    mark = models.CharField(null=False, max_length=64, verbose_name="通道标识", help_text="通道标识")
    prefix = models.CharField(max_length=32, verbose_name="被叫前缀", help_text="被叫前缀")
    cap = models.IntegerField(default=30, verbose_name="通道并发", help_text="通道并发")
    ip = models.CharField(null=False, max_length=64, verbose_name="sip地址", help_text="sip地址")
    username = models.CharField(null=False, max_length=64, verbose_name="sip账号", help_text="sip账号")
    password = models.CharField(null=False, max_length=64, verbose_name="sip密码", help_text="sip密码")

    class Meta:
        db_table = table_prefix + "sip_trunk"
        verbose_name = "通道表"
        verbose_name_plural = verbose_name


class DisNumber(CoreModel):
    number = models.CharField(null=False, max_length=64, verbose_name="号码", help_text="号码")
    area = models.CharField(null=False, max_length=64, verbose_name="区号", help_text="区号")
    code = models.CharField(max_length=32, verbose_name="岗位编码", help_text="岗位编码")
    sort = models.IntegerField(default=1, verbose_name="岗位顺序", help_text="岗位顺序")
    STATUS_CHOICES = (
        (0, "不加"),
        (1, "加"),
    )
    is_area = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name="被叫是否加区号", help_text="是否加区号 0不加、1加")
    is_zero = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name="被叫是否加0", help_text="是否加0 0不加、1加")

    trunk = models.ForeignKey(to='SipTrunk', on_delete=models.CASCADE, verbose_name='关联线路', db_constraint=False)

    class Meta:
        db_table = table_prefix + "dis_number"
        verbose_name = "号码表"
        verbose_name_plural = verbose_name


class Customer(CoreModel):
    name = models.CharField(null=False, max_length=64, verbose_name="客户名称", help_text="客户名称")
    nickname = models.CharField(max_length=32, verbose_name="客户昵称", help_text="客户昵称")
    phone = models.CharField(max_length=32, verbose_name="客户号码", help_text="客户号码")
    email = models.CharField(max_length=32, verbose_name="客户邮箱", help_text="客户邮箱")
    SEX_CHOICES = (
        (0, "女"),
        (1, "男"),
        (2, "未知"),
    )
    sex = models.IntegerField(choices=SEX_CHOICES, default=2, verbose_name="客户性别", help_text="客户性别")
    age = models.CharField(max_length=32, verbose_name="客户年龄", help_text="客户年龄")
    address = models.CharField(max_length=32, verbose_name="客户地址", help_text="客户地址")
    STATUS_CHOICES = (
        (0, "无效"),
        (1, "有效"),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="客户状态", help_text="客户状态")

    class Meta:
        db_table = table_prefix + "customer"
        verbose_name = "客户表"
        verbose_name_plural = verbose_name


class Follow(CoreModel):
    name = models.CharField(null=False, max_length=64, verbose_name="客户名称", help_text="客户名称")
    content = models.CharField(max_length=32, verbose_name="记录内容", help_text="记录内容")

    customer = models.ForeignKey(to='Customer', on_delete=models.CASCADE, verbose_name='关联客户', db_constraint=False)

    class Meta:
        db_table = table_prefix + "follow"
        verbose_name = "客户表"
        verbose_name_plural = verbose_name


class Record(CoreModel):
    username = models.CharField(null=False, max_length=64, verbose_name="账号名称", help_text="账号名称")
    ext_number = models.CharField(null=False, max_length=64, verbose_name="坐席账号", help_text="坐席账号")
    dis_number = models.CharField(null=False, max_length=64, verbose_name="外显号码", help_text="外显号码")
    call_number = models.CharField(null=False, max_length=64, verbose_name="被叫号码", help_text="被叫号码")
    start_time = models.DateTimeField(null=False, verbose_name="呼叫时间", help_text="呼叫时间")
    answer_time = models.DateTimeField(verbose_name="应答时间", help_text="应答时间")
    end_time = models.DateTimeField(null=False, verbose_name="挂机时间", help_text="挂机时间")
    bill_sec = models.IntegerField(null=False, default=0, verbose_name="通话时长", help_text="通话时长")
    record_file = models.CharField(null=False, max_length=128, verbose_name="录音文件", help_text="录音文件")
    customer_id = models.CharField(null=False, max_length=64, verbose_name="客户id", help_text="客户id")

    class Meta:
        db_table = table_prefix + "record"
        verbose_name = "通话记录表"
        verbose_name_plural = verbose_name
        ordering = ("bill_sec",)


class Report(CoreModel):
    ext_number = models.CharField(max_length=32, verbose_name="坐席号码", help_text="坐席号码")
    call_time = models.DateField(null=False, verbose_name="呼叫时间", help_text="呼叫时间")
    total = models.IntegerField(default=0, verbose_name="呼叫总数", help_text="呼叫总数")
    success = models.IntegerField(default=0, verbose_name="接通数", help_text="接通数")
    fail = models.IntegerField(default=0, verbose_name="失败数", help_text="失败数")

    class Meta:
        db_table = table_prefix + "report"
        verbose_name = "统计表"
        verbose_name_plural = verbose_name
        ordering = ("total",)


class Asr(CoreModel):
    ext_number = models.CharField(max_length=32, verbose_name="坐席账号", help_text="坐席账号")
    call_number = models.CharField(null=False, max_length=64, verbose_name="被叫号码", help_text="被叫号码")
    call_time = models.DateField(null=False, verbose_name="呼叫时间", help_text="呼叫时间")
    a_content = models.CharField(max_length=512, verbose_name="a侧内容", help_text="a侧内容")
    b_content = models.CharField(max_length=512, verbose_name="b侧内容", help_text="b侧内容")
    STATUS_CHOICES = (
        (0, "否"),
        (1, "是"),
    )
    checked = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="质检状态", help_text="质检状态")
    recognize = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="识别状态", help_text="识别状态")

    class Meta:
        db_table = table_prefix + "asr"
        verbose_name = "识别记录表"
        verbose_name_plural = verbose_name

