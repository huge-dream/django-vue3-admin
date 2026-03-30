from django.db import models

from dvadmin.utils.models import table_prefix


class QuotationMaster(models.Model):
    """杂采报价单主表（采购端比价弹窗按 autoid 拉详情用于供应商报价预览）"""

    PAYMENT_METHOD_CHOICES = (
        (1, "月结30天"),
        (2, "月结60天"),
        (3, "货到付款"),
        (4, "预付30%，余款次月结"),
    )

    STATUS_CHOICES = (
        (1, "待报价"),
        (2, "报价中"),
        (3, "已报价"),
        (4, "已过期"),
    )

    AWARD_STATUS_CHOICES = (
        (0, "未中标"),
        (1, "已中标"),
    )

    BUYING_METHOD_CHOICES = (
        (1, "询价"),
        (2, "招标"),
    )

    autoid = models.BigAutoField( primary_key=True, db_column="autoId", verbose_name="自增ID" )
    quotation_no = models.CharField( max_length=20, unique=True, db_index=True, verbose_name="报价单单号" )
    inquiry_no = models.CharField( max_length=20, db_index=True, verbose_name="询价单单号", help_text="报价单关联的询价单单号" )
    supplier_code = models.CharField( max_length=20, verbose_name="供应商代码" )
    supplier_name = models.CharField( max_length=20, verbose_name="供应商名称" )
    contact_person = models.CharField( max_length=20, null=True, blank=True, verbose_name="联系人" )
    contact_phone = models.CharField( max_length=20, null=True, blank=True, verbose_name="联系人电话" )
    contact_email = models.CharField( max_length=20, null=True, blank=True, verbose_name="联系人邮件" )
    quote_deadline = models.DateTimeField( null=True, blank=True, verbose_name="报价截止时间" )
    validity_days = models.IntegerField( null=True, blank=True, verbose_name="有效天数" )
    delivery_days = models.IntegerField( null=True, blank=True, verbose_name="交货周期" )
    payment_method = models.IntegerField( choices=PAYMENT_METHOD_CHOICES, null=True, blank=True, verbose_name="付款方式" )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1,
        null=True,
        blank=True,
        verbose_name="状态",
        help_text=(
            "1 待报价 2 报价中 3 已报价 4 已过期；"
            "置为已报价请走 POST quotation_master/{id}/submit/；"
            "超时批量置过期及询价单收口见 sync_expired / Inquiry.sync_to_quote_closed_when_no_open_quotations；"
            "名单内供应商均已提交见 submit 与 Inquiry.sync_to_quote_closed_when_all_suppliers_quoted。"
        ),
    )
    is_awarded = models.IntegerField( choices=AWARD_STATUS_CHOICES, default=0, null=True, blank=True, verbose_name="报价中标否" )
    createuser = models.CharField( max_length=20, null=True, blank=True, verbose_name="创建人员" )
    creattime = models.DateTimeField( null=True, blank=True, verbose_name="创建时间" )
    quoteuser = models.CharField( max_length=20, null=True, blank=True, verbose_name="报价人员" )
    quotetime = models.DateTimeField(
        null=True, blank=True, verbose_name="报价时间", help_text="正式提交报价时由 submit 接口写入当前时间"
    )
    remark = models.TextField( null=True, blank=True, verbose_name="报价说明及备注" )
    buying_method = models.IntegerField(choices=BUYING_METHOD_CHOICES, null=True, blank=True, verbose_name="采购方式（寻源方式）")
    bid_start_time = models.DateTimeField(null=True, blank=True, verbose_name="投标开始时间")
    bid_end_time = models.DateTimeField(null=True, blank=True, verbose_name="投标截止时间")

    class Meta:
        db_table = table_prefix + "sup_quotation_master"
        verbose_name = "杂采报价单主表"
        verbose_name_plural = verbose_name
        ordering = ("-creattime", "-autoid")

    def __str__(self):
        return self.quotation_no


class QuotationAttachment(models.Model):
    """杂采报价单-附件关联表"""

    autoid = models.BigAutoField(primary_key=True, db_column="autoId", verbose_name="自增ID")
    quotation_no = models.ForeignKey(
        QuotationMaster,
        to_field="quotation_no",
        db_column="quotation_no",
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="报价单单号",
    )
    part_id = models.CharField(max_length=50, db_column="Partid", verbose_name="产品料号")
    file_name = models.CharField(max_length=100, db_column="file_name", verbose_name="文件名称")
    file_path = models.CharField(max_length=200, db_column="file_path", null=True, blank=True, verbose_name="文件路径")
    uploadtime = models.CharField(max_length=20, null=True, blank=True, verbose_name="上传时间")
    uploaduser = models.CharField(max_length=20, null=True, blank=True, verbose_name="上传人员")

    class Meta:
        db_table = table_prefix + "sup_quotation_attachment"
        verbose_name = "杂采报价单-附件关联表"
        verbose_name_plural = verbose_name
        ordering = ("-autoid",)
        unique_together = ("quotation_no", "part_id", "file_name")

    def __str__(self):
        return self.file_name


class QuotationMaterial(models.Model):
    """杂采报价单-材料成本明细表"""

    autoid = models.BigAutoField(primary_key=True, db_column="autoId", verbose_name="自增ID")
    quotation_no = models.ForeignKey(
        QuotationMaster,
        to_field="quotation_no",
        db_column="quotation_no",
        on_delete=models.CASCADE,
        related_name="material_costs",
        verbose_name="报价单单号",
    )
    part_id = models.CharField(max_length=50, db_column="Partid", verbose_name="产品料号")
    material_spec = models.CharField(max_length=20, db_column="material_spec", verbose_name="材料规格")
    length = models.CharField(max_length=10, db_column="Length", null=True, blank=True, verbose_name="长")
    width = models.CharField(max_length=10, db_column="Width", null=True, blank=True, verbose_name="宽")
    height = models.CharField(max_length=10, db_column="Height", null=True, blank=True, verbose_name="高")
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="UnitPrice",
        null=True,
        blank=True,
        verbose_name="单价",
    )
    qty = models.IntegerField(db_column="qty", null=True, blank=True, verbose_name="数量")
    specific_gravity = models.CharField(
        max_length=10,
        db_column="SpecificGravity",
        null=True,
        blank=True,
        verbose_name="比重",
    )
    material_cost = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="material_cost",
        null=True,
        blank=True,
        verbose_name="材料费用",
    )
    weight = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="Weight",
        null=True,
        blank=True,
        verbose_name="重量",
    )
    remark = models.CharField(max_length=100, db_column="remark", null=True, blank=True, verbose_name="备注")
    option_json = models.TextField(db_column="OptionJson", null=True, blank=True, verbose_name="可选扩展信息")

    class Meta:
        db_table = table_prefix + "sup_quotation_material"
        verbose_name = "杂采报价单-材料成本明细表"
        verbose_name_plural = verbose_name
        ordering = ("autoid",)
        unique_together = ("quotation_no", "part_id", "material_spec")
        indexes = [
            models.Index(fields=["part_id"]),
        ]

    def __str__(self):
        return f"{self.quotation_no_id}-{self.part_id}-{self.material_spec}"


class QuotationProcess(models.Model):
    """杂采报价单-加工成本明细表"""

    autoid = models.BigAutoField(primary_key=True, db_column="autoId", verbose_name="自增ID")
    quotation_no = models.ForeignKey(
        QuotationMaster,
        to_field="quotation_no",
        db_column="quotation_no",
        on_delete=models.CASCADE,
        related_name="process_costs",
        verbose_name="报价单单号",
    )
    part_id = models.CharField(max_length=50, db_column="Partid", verbose_name="产品料号")
    process_station = models.CharField(
        max_length=20,
        db_column="process_station",
        null=True,
        blank=True,
        verbose_name="加工工站",
    )
    # 单位为文本（如 PCS/小时/cm），与 miscprocurement.InquiryProcessCost 一致
    unit = models.CharField(
        max_length=20,
        db_column="Unit",
        null=True,
        blank=True,
        verbose_name="单位",
    )
    unit_rate = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="UnitRate",
        null=True,
        blank=True,
        verbose_name="费率",
    )
    process_qty = models.CharField(max_length=20, db_column="ProcessQty", null=True, blank=True, verbose_name="加工计量")
    process_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="ProcessPrice",
        null=True,
        blank=True,
        verbose_name="加工费用",
    )
    remark = models.CharField(max_length=100, db_column="remark", null=True, blank=True, verbose_name="备注")
    option_json = models.TextField(db_column="OptionJson", null=True, blank=True, verbose_name="可选扩展信息")

    class Meta:
        db_table = table_prefix + "sup_quotation_process"
        verbose_name = "杂采报价单-加工成本明细表"
        verbose_name_plural = verbose_name
        ordering = ("autoid",)
        unique_together = ("quotation_no", "part_id", "process_station")
        indexes = [
            models.Index(fields=["part_id"]),
        ]

    def __str__(self):
        return f"{self.quotation_no_id}-{self.part_id}-{self.process_station}"


class QuotationOther(models.Model):
    """杂采报价单-其他费用明细表"""

    autoid = models.BigAutoField(primary_key=True, db_column="autoId", verbose_name="自增ID")
    quotation_no = models.ForeignKey(
        QuotationMaster,
        to_field="quotation_no",
        db_column="quotation_no",
        on_delete=models.CASCADE,
        related_name="other_costs",
        verbose_name="报价单单号",
    )
    part_id = models.CharField(max_length=50, db_column="Partid", verbose_name="产品料号")
    packaging_cost = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="packaging_cost",
        null=True,
        blank=True,
        verbose_name="包装费用",
    )
    transportation_cost = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="transportation_cost",
        null=True,
        blank=True,
        verbose_name="运输费用",
    )

    class Meta:
        db_table = table_prefix + "sup_quotation_other"
        verbose_name = "杂采报价单-其他费用明细表"
        verbose_name_plural = verbose_name
        ordering = ("autoid",)
        indexes = [
            models.Index(fields=["part_id"]),
        ]

    def __str__(self):
        return f"{self.quotation_no_id}-{self.part_id}"


class QuotationProfit(models.Model):
    """杂采报价单-税率利润明细表"""

    autoid = models.BigAutoField(primary_key=True, db_column="autoId", verbose_name="自增ID")
    quotation_no = models.ForeignKey(
        QuotationMaster,
        to_field="quotation_no",
        db_column="quotation_no",
        on_delete=models.CASCADE,
        related_name="profit_costs",
        verbose_name="报价单单号",
    )
    part_id = models.CharField(max_length=50, db_column="Partid", verbose_name="产品料号")
    tax_rate = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="tax_rate",
        null=True,
        blank=True,
        verbose_name="税率",
    )
    profit_rate = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="profit_rate",
        null=True,
        blank=True,
        verbose_name="利润率",
    )

    class Meta:
        db_table = table_prefix + "sup_quotation_profit"
        verbose_name = "杂采报价单-税率利润明细表"
        verbose_name_plural = verbose_name
        ordering = ("autoid",)
        indexes = [
            models.Index(fields=["part_id"]),
        ]

    def __str__(self):
        return f"{self.quotation_no_id}-{self.part_id}"


class QuotationItem(models.Model):
    """杂采报价单-上阶物料明细表"""

    ITEM_AWARD_STATUS_CHOICES = (
        (0, "未中标"),
        (1, "中标"),
    )

    autoid = models.BigAutoField(primary_key=True, db_column="autoId", verbose_name="自增ID")
    quotation_no = models.ForeignKey(
        QuotationMaster,
        to_field="quotation_no",
        db_column="quotation_no",
        on_delete=models.CASCADE,
        related_name="rfq_items",
        verbose_name="报价单单号",
    )
    part_id = models.CharField(max_length=50, db_column="Partid", verbose_name="产品料号")
    product_name = models.CharField(max_length=20, db_column="product_name", verbose_name="产品名称")
    unit = models.CharField(max_length=10, db_column="unit", verbose_name="计量单位")
    qty = models.IntegerField(db_column="qty", verbose_name="采购数量")
    is_bom = models.IntegerField(db_column="IsBom", verbose_name="是否成本结构")
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="unit_price",
        null=True,
        blank=True,
        verbose_name="标准品单价",
    )
    product_cost = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="product_cost",
        null=True,
        blank=True,
        verbose_name="标准品总价",
    )
    total_material_cost = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="total_material_cost",
        null=True,
        blank=True,
        verbose_name="材料成本合计",
    )
    total_processing_cost = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="total_processing_cost",
        null=True,
        blank=True,
        verbose_name="加工成本合计",
    )
    total_other_expense = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="total_other_expense",
        null=True,
        blank=True,
        verbose_name="其他费用合计",
    )
    total_opex_amt = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="total_opex_amt",
        null=True,
        blank=True,
        verbose_name="管销研费用",
    )
    profit_rate = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="profit_rate",
        null=True,
        blank=True,
        verbose_name="利润",
    )
    total_price_excl_tax = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="total_price_excl_tax",
        null=True,
        blank=True,
        verbose_name="不含税总价",
    )
    tax_rate = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="tax_rate",
        null=True,
        blank=True,
        verbose_name="税费",
    )
    total_price_incl_tax = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="total_price_incl_tax",
        null=True,
        blank=True,
        verbose_name="含税总价",
    )
    is_awarded = models.IntegerField(
        choices=ITEM_AWARD_STATUS_CHOICES,
        db_column="is_awarded",
        null=True,
        blank=True,
        verbose_name="报价中标否",
    )
    winning_bid_price = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        db_column="winning_bid_price",
        null=True,
        blank=True,
        verbose_name="中标价格",
    )

    class Meta:
        db_table = table_prefix + "sup_quot_items"
        verbose_name = "杂采报价单-上阶物料明细表"
        verbose_name_plural = verbose_name
        ordering = ("autoid",)
        indexes = [
            models.Index(fields=["part_id"]),
        ]

    def __str__(self):
        return f"{self.quotation_no_id}-{self.part_id}"
