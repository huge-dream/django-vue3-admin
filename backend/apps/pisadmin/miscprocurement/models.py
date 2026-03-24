from django.db import models

from dvadmin.utils.models import CoreModel, table_prefix


class MiscProcurementMaterialInfo(CoreModel):
    """杂采材料信息"""

    factory = models.CharField(max_length=10, verbose_name="交易厂区", help_text="交易厂区(公司)", null=True, blank=True)
    materialtype = models.CharField(max_length=50, verbose_name="材质", help_text="材质", null=True, blank=True)
    density = models.CharField(max_length=20, verbose_name="比重", help_text="比重")
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="单价", help_text="单价")
    status = models.IntegerField(default=1, verbose_name="可用状态", help_text="可用状态(1可用0不可用)")

    class Meta:
        db_table = table_prefix + "misc_procurement_material_info"
        verbose_name = "杂采材料信息"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)

    def __str__(self):
        return self.materialtype or ""


class MiscProcurementStationInfo(CoreModel):
    """杂采工站信息"""

    company_code = models.CharField(max_length=10, verbose_name="交易厂区", help_text="交易厂区(公司)", null=True, blank=True)
    stationname = models.CharField(max_length=50, verbose_name="工站名称", help_text="工站名称")
    stationcode = models.CharField(max_length=20, verbose_name="工站代码", help_text="工站代码", null=True, blank=True)
    stationtype = models.IntegerField(verbose_name="工站类型归属", help_text="工站类型归属(1:模治具 2:石墨)")
    unit = models.CharField(max_length=20, verbose_name="计量单位", help_text="计量单位", null=True, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="费率", help_text="费率")
    status = models.IntegerField(default=1, verbose_name="可用状态", help_text="可用状态(1可用0不可用)")

    class Meta:
        db_table = table_prefix + "misc_procurement_station_info"
        verbose_name = "杂采加工工站信息"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)

    def __str__(self):
        return self.stationname


class MiscProcMaterial(CoreModel):
    """杂采料号信息"""

    company_code = models.CharField(max_length=10, verbose_name="交易厂区", help_text="交易厂区(公司)", null=True, blank=True)
    partid = models.CharField(max_length=50, verbose_name="料号", help_text="料号(物料编码)", null=True, blank=True)
    partid_name = models.CharField(max_length=50, verbose_name="物料说明", help_text="物料说明")
    specification = models.CharField(max_length=50, verbose_name="品名规格", help_text="品名规格")
    unit = models.CharField(max_length=50, verbose_name="单位", help_text="单位")
    partid_category_id = models.IntegerField(verbose_name="物料分类", help_text="物料分类(1：模治具，2：石墨  3：)", null=True, blank=True)
    status = models.IntegerField(default=1, verbose_name="启用否", help_text="启用否(1:启用 0 禁用)")

    class Meta:
        db_table = table_prefix + "misc_proc_materials"
        verbose_name = "杂采料号信息"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime",)

    def __str__(self):
        return self.partid or self.partid_name


class CostEstimateTemplateHead(models.Model):
    """成本估算模板主表；确认某一版本时，同 template_no 下更低版本的主表行由接口批量改为作废(2)。"""
    STATUS_CHOICES = (
        (0, "未确认"),
        (1, "已确认"),
        (2, "作废"),
    )

    template_no = models.CharField(max_length=20, db_index=True, db_column="TemplateNo", verbose_name="模板编号")
    template_name = models.CharField(max_length=50, db_column="TemplateName", verbose_name="模板名称")
    procurement_category = models.CharField(max_length=4, db_column="ProcurementCategory", verbose_name="采购类别：1-策采；2-杂采")
    is_bom = models.CharField(max_length=4, db_column="IsBom", verbose_name="启用BOM否")
    acti = models.CharField(max_length=4, db_column="Acti", null=True, blank=True, default="Y", verbose_name="有效否：Y/N")
    # 允许为空：前端备注可不填
    template_desc = models.CharField(max_length=500, db_column="TemplateDesc", null=True, blank=True, verbose_name="模板描述")
    is_can_add_materials = models.IntegerField(db_column="IsCanAddMaterials", default=0, verbose_name="材料允许供应商增行")
    is_can_add_process = models.IntegerField(db_column="IsCanAddprocess", default=0, verbose_name="加工允许供应商增行")
    create_user = models.CharField(max_length=20, db_column="CreateUser", null=True, blank=True, verbose_name="创建人")
    create_time = models.DateTimeField(db_column="CreateTime", null=True, blank=True, verbose_name="创建时间")
    update_user = models.CharField(max_length=20, db_column="UpdateUser", null=True, blank=True, verbose_name="最后更新人")
    update_time = models.DateTimeField(db_column="UpdateTime", null=True, blank=True, verbose_name="最后更新时间")
    version = models.IntegerField(db_column="Version", default=1, verbose_name="版本号")
    status = models.IntegerField(db_column="Status", default=0, verbose_name="状态", choices=STATUS_CHOICES)

    class Meta:
        db_table = "t_CostEstimate_Template_Head"
        verbose_name = "成本估算模板主表"
        verbose_name_plural = verbose_name
        ordering = ("-update_time", "-id")
        indexes = [
            models.Index(fields=["template_no", "version"], name="idx_cost_template_head_no_ver"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=("template_no", "version"),
                name="uq_cost_template_head_no_ver",
            ),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return self.template_name

    @property
    def items(self):
        """明细表按 (template_no, version) 与当前主表行对齐（非 ORM 反向关联）。"""
        return CostEstimateTemplateBody.objects.filter(
            template_no=self.template_no,
            version=self.version,
        ).order_by("item_order", "id")


class CostEstimateTemplateBody(models.Model):
    COST_CATEGORY_CHOICES = (
        ("1", "材料成本"),
        ("2", "加工成本"),
        ("3", "其它成本"),
        ("4", "管销研成本"),
        ("5", "利润成本"),
        ("6", "税费成本"),
        ("7", "产品明细"),
    )

    SUPPLIER_REQUIRED_CHOICES = (
        (0, " "),
        (1, "带出不可修改"),
        (2, "带出可修改"),
        (3, "不带出必填"),
        (4, "不带出可空"),
        (5, "必填"),
        (6, "可空"),
    )

    # 与主表通过 (template_no, version) 逻辑关联；主表上该组合唯一（见 CostEstimateTemplateHead.Meta.constraints）
    template_no = models.CharField(max_length=20, db_column="TemplateNo", verbose_name="模板编号")
    cost_category = models.CharField(max_length=4, choices=COST_CATEGORY_CHOICES, db_column="CostCategory", verbose_name="成本类别")
    item_order = models.IntegerField(db_column="ItemOrder", verbose_name="排序序号")
    item_no = models.CharField(max_length=100, db_column="ItemNo", verbose_name="项次编号")
    item_name_cn = models.CharField(max_length=100, db_column="ItemName_cn", verbose_name="中文名称")
    item_name_en = models.CharField(max_length=100, db_column="ItemName_en", null=True, blank=True, verbose_name="英文名称")
    item_name_vn = models.CharField(max_length=100, db_column="ItemName_vn", null=True, blank=True, verbose_name="越南语名称")
    is_fixed = models.IntegerField(db_column="is_fixed", verbose_name="是否固定字段：1是0否")
    is_computed = models.IntegerField(db_column="is_computed", verbose_name="是否系统自动计算/带出")
    purchaser_required = models.IntegerField(db_column="PurchaserRequired", verbose_name="采购必填否(1/0)")
    supplier_required = models.IntegerField(db_column="SupplierRequired", choices=SUPPLIER_REQUIRED_CHOICES, verbose_name="供应商操作")
    remark = models.CharField(max_length=200, db_column="Remark", null=True, blank=True, verbose_name="备注")
    create_user = models.CharField(max_length=20, db_column="CreateUser", null=True, blank=True, verbose_name="创建人")
    create_time = models.DateTimeField(db_column="CreateTime", null=True, blank=True, verbose_name="创建时间")
    update_user = models.CharField(max_length=20, db_column="UpdateUser", null=True, blank=True, verbose_name="最后更新人")
    update_time = models.DateTimeField(db_column="UpdateTime", null=True, blank=True, verbose_name="最后更新时间")
    version = models.IntegerField(db_column="Version", default=1, verbose_name="版本号")

    class Meta:
        db_table = "t_CostEstimate_Template_Body"
        verbose_name = "成本估算模板明细"
        verbose_name_plural = verbose_name
        ordering = ("item_order", "id")
        indexes = [
            models.Index(fields=["template_no", "version"], name="idx_cost_template_body_no_ver"),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return self.item_no


class Inquiry(CoreModel):
    """杂采询价单主表"""
    
    # (1开立；2确认；3发布；4报价中；5报价结束；6比议价中；7价格审核；8核价通过(结束)；9落标(结束)；0作废)
    STATUS_CHOICES = (
        (1, "开立"),
        (2, "确认"),
        (3, "发布"),
        (4, "报价中"),
        (5, "报价结束"),
        (6, "比议价中"),
        (7, "价格审核"),
        (8, "核价通过(结束)"),
        (9, "落标(结束)"),
        (0, "作废"),
    )
    PAYMENT_METHOD_CHOICES = (
        (1, "月结30天"),
        (2, "月结60天"),
        (3, "不到付款"),
        (4, "预付30%"),
        (5, "预付50%"),
        (6, "余款至生产"),
        (7, "价格审核"),
        (8, "价格结算(运费)"),
        (9, "新建(结束)"),
    )
    PURCHASE_TYPE_CHOICES = (
        (1, "策采"),
        (2, "杂采"),
    )
    CATEGORY_CHOICES = (
        (1, "中压"),
        (2, "活塞"),
        (3, "模具/夹具"),
        (4, "管"),
    )

    inquiry_no = models.CharField(max_length=20, unique=True, db_index=True, verbose_name="询价单号")
    title = models.CharField(max_length=20, verbose_name="询价单名称")
    purchase_type = models.IntegerField(choices=PURCHASE_TYPE_CHOICES, verbose_name="采购类别")
    material_type = models.CharField(max_length=20, null=True, blank=True, verbose_name="材料类型")
    template = models.CharField(
        max_length=20,
        verbose_name="询价模版",
        help_text="对应成本估算模板编号；发布生成供应商报价单时，子表字段是否从询价单带入由该模板明细 is_computed=1 或 supplier_required 为 1/2 决定。",
    )
    is_bom = models.IntegerField(default=0, verbose_name="是否BOM否")
    currency = models.CharField(max_length=20, default="CNY", verbose_name="交易币别")
    company_code = models.CharField(max_length=20, null=True, blank=True, verbose_name="公司代码")
    purchase_dept = models.CharField(max_length=20, null=True, blank=True, verbose_name="采购部门")
    buyer = models.CharField(max_length=20, verbose_name="采购负责人")
    quote_deadline = models.DateTimeField(null=True, blank=True, verbose_name="报价截止时间")
    target_price = models.DecimalField(db_column="target_price", max_digits=12, decimal_places=4, default=0, verbose_name="目标价格")
    lead_time_days = models.IntegerField(default=0, verbose_name="交货周期(天)")
    payment_method = models.IntegerField(choices=PAYMENT_METHOD_CHOICES, verbose_name="付款方式")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, db_index=True, verbose_name="状态")
    confirm_user = models.CharField(max_length=20, null=True, blank=True, verbose_name="确认人")
    confirm_time = models.DateTimeField(null=True, blank=True, verbose_name="确认时间")
    release_user = models.CharField(max_length=20, null=True, blank=True, verbose_name="发布人")
    release_time = models.DateTimeField(null=True, blank=True, verbose_name="发布时间")
    comparison_user = models.CharField(max_length=20, null=True, blank=True, verbose_name="比价人")
    comparison_time = models.DateTimeField(null=True, blank=True, verbose_name="比价时间")
    win_supplier_code = models.CharField(max_length=20, null=True, blank=True, verbose_name="中标供应商代码")
    win_price = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, verbose_name="中标价格")
    approval_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="EIP审核单号")
    approval_status = models.IntegerField(null=True, blank=True, verbose_name="EIP审核结果")
    remark = models.CharField(max_length=100, null=True, blank=True, verbose_name="备注")
    create_time = models.DateTimeField(db_column="createtime", auto_now_add=True, verbose_name="创建时间")
    create_user = models.CharField(max_length=20, db_column="createuser", null=True, blank=True, verbose_name="创建人")
    update_user = models.CharField(max_length=20, db_column="UpdateUser", null=True, blank=True, verbose_name="最后更新人")
    update_time = models.DateTimeField(db_column="UpdateTime", null=True, blank=True, verbose_name="最后更新时间")

    class Meta:
        db_table = table_prefix + "proc_inquiry_master"
        verbose_name = "询价单"
        verbose_name_plural = verbose_name
        ordering = ("-create_time", "-id")

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return self.inquiry_no


class InquirySupplier(models.Model):
    """杂采询价单-供应商关联表"""
    
    inquiry_no = models.ForeignKey(
        Inquiry,
        to_field="inquiry_no",
        db_column="inquiry_no",
        on_delete=models.CASCADE,
        related_name="suppliers",
        verbose_name="询价单号",
    )
    part_id = models.CharField(max_length=50, db_column="PartId", verbose_name="产品料号")
    supplier_code = models.CharField(max_length=20, db_column="supplier_code", verbose_name="供应商代码")
    supplier_name = models.CharField(max_length=50, db_column="supplier_name", verbose_name="供应商名称")
    contact_person = models.CharField(max_length=20, db_column="contact_person", null=True, blank=True, verbose_name="联系人")
    contact_phone = models.CharField(max_length=20, db_column="contact_phone", null=True, blank=True, verbose_name="联系电话")
    contact_email = models.CharField(max_length=50, db_column="contact_email", null=True, blank=True, verbose_name="联系邮箱")
    create_time = models.DateTimeField(db_column="createtime", auto_now_add=True, verbose_name="添加时间")
    create_user = models.CharField(max_length=20, db_column="createuser", null=True, blank=True, verbose_name="添加人")

    class Meta:
        db_table = table_prefix + "proc_inquiry_supplier"
        verbose_name = "杂采询价单-供应商关联表"
        verbose_name_plural = verbose_name
        unique_together = ("inquiry_no", "part_id", "supplier_code")
        ordering = ("id",)

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return self.supplier_name


class InquiryAttachment(models.Model):
    """杂采询价单-附件关联表"""
    
    FILE_TYPE_CHOICES = (
        (1, "产品图纸"),
        (2, "招标文件"),
        (3, "其它文件"),
    )

    inquiry_no = models.ForeignKey(
        Inquiry,
        to_field="inquiry_no",
        db_column="inquiry_no",
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="询价单号",
    )
    part_id = models.CharField(max_length=50, db_column="PartId", verbose_name="产品料号")
    file_type = models.IntegerField(choices=FILE_TYPE_CHOICES, db_column="file_type", verbose_name="文件类型")
    file_name = models.CharField(max_length=100, db_column="file_name", verbose_name="文件名称")
    file_path = models.CharField(max_length=200, db_column="file_path", verbose_name="文件路径")
    upload_time = models.DateTimeField(db_column="uploadtime", auto_now_add=True, verbose_name="上传时间")
    upload_user = models.CharField(max_length=20, db_column="uploaduser", null=True, blank=True, verbose_name="上传人")

    class Meta:
        db_table = table_prefix + "proc_inquiry_attachment"
        verbose_name = "杂采询价单-附件关联表"
        verbose_name_plural = verbose_name
        unique_together = ("inquiry_no", "part_id", "file_name")
        ordering = ("-upload_time",)

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return self.file_name


class InquiryMaterialCost(models.Model):
    """杂采询价单-材料成本明细表"""

    inquiry_no = models.ForeignKey(
        Inquiry,
        to_field="inquiry_no",
        db_column="inquiry_no",
        on_delete=models.CASCADE,
        related_name="material_costs",
        verbose_name="询价单号",
    )
    part_id = models.CharField(max_length=50, db_column="PartId", verbose_name="产品料号")
    material_spec = models.CharField(max_length=20, db_column="material_spec", null=True, blank=True, verbose_name="材料规格")
    length = models.CharField(max_length=10, db_column="Length", null=True, blank=True, verbose_name="长")
    width = models.CharField(max_length=10, db_column="Width", null=True, blank=True, verbose_name="宽")
    height = models.CharField(max_length=10, db_column="Height", null=True, blank=True, verbose_name="高")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, db_column="UnitPrice", null=True, blank=True, verbose_name="单价")
    qty = models.IntegerField(db_column="qty", null=True, blank=True, verbose_name="数量")
    specific_gravity = models.CharField(
        max_length=10, db_column="SpecificGravity", null=True, blank=True, verbose_name="比重"
    )
    material_cost = models.DecimalField(
        max_digits=12, decimal_places=4, db_column="material_cost", null=True, blank=True, verbose_name="材料费用"
    )
    remark = models.CharField(max_length=100, db_column="remark", null=True, blank=True, verbose_name="备注")
    option_json = models.TextField(db_column="OptionJson", null=True, blank=True, verbose_name="可选扩展信息")
    create_time = models.DateTimeField(db_column="createtime", auto_now_add=True, verbose_name="创建时间")
    create_user = models.CharField(max_length=20, db_column="createuser", null=True, blank=True, verbose_name="创建人")

    class Meta:
        db_table = table_prefix + "proc_inquiry_material_cost"
        verbose_name = "杂采询价单-材料成本明细表"
        verbose_name_plural = verbose_name
        ordering = ("id",)
        indexes = [
            models.Index(fields=["part_id"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"{self.inquiry_no_id}-{self.part_id}"


class InquiryProcessCost(models.Model):
    """杂采询价单-加工成本明细表"""

    inquiry_no = models.ForeignKey(
        Inquiry,
        to_field="inquiry_no",
        db_column="inquiry_no",
        on_delete=models.CASCADE,
        related_name="process_costs",
        verbose_name="询价单号",
    )
    part_id = models.CharField(max_length=50, db_column="PartId", verbose_name="产品料号")
    process_station = models.CharField(
        max_length=20, db_column="process_station", null=True, blank=True, verbose_name="加工工站"
    )
    # 单位为文本（如 PCS/小时/次），历史误建为 DecimalField 会导致前端传字符串时报校验错误
    unit = models.CharField(max_length=20, db_column="Unit", null=True, blank=True, verbose_name="单位")
    unit_rate = models.DecimalField(
        max_digits=12, decimal_places=4, db_column="UnitRate", null=True, blank=True, verbose_name="费率"
    )
    process_qty = models.CharField(max_length=20, db_column="ProcessQty", null=True, blank=True, verbose_name="加工数量")
    process_price = models.DecimalField(
        max_digits=10, decimal_places=2, db_column="ProcessPrice", null=True, blank=True, verbose_name="加工费用"
    )
    remark = models.CharField(max_length=100, db_column="remark", null=True, blank=True, verbose_name="备注")
    option_json = models.TextField(db_column="OptionJson", null=True, blank=True, verbose_name="可选扩展信息")
    create_time = models.DateTimeField(db_column="createtime", auto_now_add=True, verbose_name="创建时间")
    create_user = models.CharField(max_length=20, db_column="createuser", null=True, blank=True, verbose_name="创建人")

    class Meta:
        db_table = table_prefix + "proc_inquiry_process_cost"
        verbose_name = "杂采询价单-加工成本明细表"
        verbose_name_plural = verbose_name
        ordering = ("id",)
        indexes = [
            models.Index(fields=["part_id"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"{self.inquiry_no_id}-{self.part_id}"


class InquiryOtherCost(models.Model):
    """杂采询价单-其它成本明细表"""

    inquiry_no = models.ForeignKey(
        Inquiry,
        to_field="inquiry_no",
        db_column="inquiry_no",
        on_delete=models.CASCADE,
        related_name="other_costs",
        verbose_name="询价单号",
    )
    part_id = models.CharField(max_length=50, db_column="PartId", verbose_name="产品料号")
    packaging_cost = models.DecimalField(
        max_digits=12, decimal_places=4, db_column="packaging_cost", null=True, blank=True, verbose_name="包装费用"
    )
    transportation_cost = models.DecimalField(
        max_digits=12, decimal_places=4, db_column="transportation_cost", null=True, blank=True, verbose_name="运输费用"
    )
    create_time = models.DateTimeField(db_column="createtime", auto_now_add=True, verbose_name="创建时间")
    create_user = models.CharField(max_length=20, db_column="createuser", null=True, blank=True, verbose_name="创建人")

    class Meta:
        db_table = table_prefix + "proc_inquiry_other_cost"
        verbose_name = "杂采询价单-其它成本明细表"
        verbose_name_plural = verbose_name
        ordering = ("id",)
        indexes = [
            models.Index(fields=["part_id"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"{self.inquiry_no_id}-{self.part_id}"


class InquiryProfitCost(models.Model):
    """杂采询价单-税费利润明细表"""

    inquiry_no = models.ForeignKey(
        Inquiry,
        to_field="inquiry_no",
        db_column="inquiry_no",
        on_delete=models.CASCADE,
        related_name="profit_costs",
        verbose_name="询价单号",
    )
    part_id = models.CharField(max_length=50, db_column="PartId", verbose_name="产品料号")
    tax_rate = models.DecimalField(
        max_digits=12, decimal_places=4, db_column="tax_rate", null=True, blank=True, verbose_name="税率"
    )
    profit_rate = models.DecimalField(
        max_digits=12, decimal_places=4, db_column="profit_rate", null=True, blank=True, verbose_name="利润率"
    )
    create_time = models.DateTimeField(db_column="createtime", auto_now_add=True, verbose_name="创建时间")
    create_user = models.CharField(max_length=20, db_column="createuser", null=True, blank=True, verbose_name="创建人")

    class Meta:
        db_table = table_prefix + "proc_inquiry_profit_cost"
        verbose_name = "杂采询价单-税费利润明细表"
        verbose_name_plural = verbose_name
        ordering = ("id",)
        indexes = [
            models.Index(fields=["part_id"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"{self.inquiry_no_id}-{self.part_id}"


class InquiryRfqItem(models.Model):
    """杂采询价单-上阶物料明细表（采购产品明细）"""

    inquiry_no = models.ForeignKey(
        Inquiry,
        to_field="inquiry_no",
        db_column="inquiry_no",
        on_delete=models.CASCADE,
        related_name="rfq_items",
        verbose_name="询价单号",
    )
    part_id = models.CharField(max_length=50, db_column="Partid", verbose_name="产品料号")
    product_name = models.CharField(max_length=20, db_column="product_name", null=True, blank=True, verbose_name="产品名称")
    unit = models.CharField(max_length=10, db_column="unit", null=True, blank=True, verbose_name="计量单位")
    qty = models.IntegerField(db_column="qty", null=True, blank=True, verbose_name="需求数量数量")
    is_bom = models.IntegerField(db_column="IsBom", null=True, blank=True, verbose_name="是否成本结构")
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=4, db_column="unit_price", null=True, blank=True, verbose_name="标准品单价"
    )
    total_material_cost = models.DecimalField(
        max_digits=12, decimal_places=4, db_column="total_material_cost", null=True, blank=True, verbose_name="材料成本合计"
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
        max_digits=12, decimal_places=4, db_column="total_other_expense", null=True, blank=True, verbose_name="其他费用合计"
    )
    total_opex_amt = models.DecimalField(
        max_digits=12, decimal_places=4, db_column="total_opex_amt", null=True, blank=True, verbose_name="管销研费用"
    )
    profit_rate = models.DecimalField(
        max_digits=12, decimal_places=4, db_column="profit_rate", null=True, blank=True, verbose_name="利润"
    )
    total_price_excl_tax = models.DecimalField(
        max_digits=12, decimal_places=4, db_column="total_price_excl_tax", null=True, blank=True, verbose_name="不含税总价"
    )
    tax_rate = models.DecimalField(
        max_digits=12, decimal_places=4, db_column="tax_rate", null=True, blank=True, verbose_name="税费"
    )
    total_price_incl_tax = models.DecimalField(
        max_digits=12, decimal_places=4, db_column="total_price_incl_tax", null=True, blank=True, verbose_name="含税总价"
    )
    option_json = models.TextField(db_column="OptionJson", null=True, blank=True, verbose_name="可选扩展信息")
    create_time = models.DateTimeField(db_column="createtime", auto_now_add=True, verbose_name="创建时间")
    create_user = models.CharField(max_length=20, db_column="createuser", null=True, blank=True, verbose_name="创建人")

    class Meta:
        db_table = table_prefix + "misc_rfq_items"
        verbose_name = "杂采询价单-上阶物料明细表"
        verbose_name_plural = verbose_name
        ordering = ("id",)
        indexes = [
            models.Index(fields=["part_id"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"{self.inquiry_no_id}-{self.part_id}"
