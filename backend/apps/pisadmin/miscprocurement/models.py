import logging
from typing import Iterable, Optional

from django.db import models
from django.utils import timezone

from dvadmin.utils.models import CoreModel, table_prefix

logger = logging.getLogger(__name__)


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
    """杂采询价单主表

    与供应商端报价联动：当全部报价单都不再处于待报价/报价中时，「发布」「报价中」可经
    `Inquiry.sync_to_quote_closed_when_no_open_quotations` 收口为「报价结束」；
    当供应商名单中每家均有一条「已报价」报价单时，可经 `Inquiry.sync_to_quote_closed_when_all_suppliers_quoted` 收口（见 `submit`）。
    """

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
    BUYING_METHOD_CHOICES = (
        (1, "询价"),
        (2, "招标"),
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
    template_version = models.IntegerField(
        db_column="TemplateVersion",
        default=1,
        verbose_name="模板版本号",
        help_text="与 template 共同锁定成本估算模板主表版本（CostEstimateTemplateHead.version）；发布与供应商报价结构均以此为准。",
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
    buying_method = models.IntegerField(choices=BUYING_METHOD_CHOICES, null=True, blank=True, verbose_name="采购方式（寻源方式）")
    bid_start_time = models.DateTimeField(null=True, blank=True, verbose_name="投标开始时间")
    bid_end_time = models.DateTimeField(null=True, blank=True, verbose_name="投标截止时间")

    class Meta:
        db_table = table_prefix + "misc_proc_inquiry_master"
        verbose_name = "询价单"
        verbose_name_plural = verbose_name
        ordering = ("-create_time", "-id")

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return self.inquiry_no

    @classmethod
    def sync_to_quote_closed_when_no_open_quotations(
        cls,
        inquiry_nos: Iterable[str],
        *,
        actor_username: Optional[str] = None,
    ) -> int:
        """
        当某询价单下已不存在「待报价」(1) 或「报价中」(2) 的报价单时，若询价单仍为「发布」(3) 或「报价中」(4)，
        则置为「报价结束」(5)，并写操作日志。

        典型调用：供应商报价单因超过截止时间被批量置为「已过期」后，判断询价维度是否可收口为报价结束。
        """
        from apps.pissupplier.models import QuotationMaster  # 避免 apps 间循环 import

        now = timezone.now()
        username = (str(actor_username).strip()[:20] if actor_username else None) or None
        unique = {str(x).strip() for x in inquiry_nos if x and str(x).strip()}
        n = 0
        for inq_no in unique:
            if QuotationMaster.objects.filter(inquiry_no=inq_no, status__in=(1, 2)).exists():
                continue
            inq = cls.objects.filter(inquiry_no=inq_no, status__in=(3, 4)).first()
            if not inq:
                continue
            old_status = int(inq.status if inq.status is not None else 0)
            inq.status = 5
            inq.update_time = now
            inq.update_datetime = now
            if username:
                inq.update_user = username
            inq.save(update_fields=["status", "update_time", "update_user", "update_datetime"])
            RFQOperationLogs.try_append(
                inquiry_no=inq.inquiry_no,
                purchase_type=int(inq.purchase_type),
                operation_type=6,
                operation_user=username,
                quotation_no="-",
                per_status=old_status,
                cur_status=5,
                operation_desc="超过报价截止时间，询价单截止报价",
            )
            n += 1
        return n

    @classmethod
    def sync_to_quote_closed_when_all_suppliers_quoted(
        cls,
        inquiry_no: str,
        *,
        actor_username: Optional[str] = None,
        quotation_no: Optional[str] = None,
    ) -> bool:
        """
        若询价单供应商名单（InquirySupplier）中每个供应商在 `QuotationMaster` 上均有一条「已报价」(3) 记录，
        且询价单仍为「发布」(3) 或「报价中」(4)，则将询价单置为「报价结束」(5)。

        用于最后一户提交正式报价后收口，不依赖是否已超过报价截止时间。
        """
        from apps.pissupplier.models import QuotationMaster  # 避免 apps 间循环 import

        inq_no = (inquiry_no or "").strip()
        if not inq_no:
            return False
        inq = cls.objects.filter(inquiry_no=inq_no, status__in=(3, 4)).first()
        if not inq:
            return False

        raw_codes = (
            InquirySupplier.objects.filter(inquiry_no=inq_no)
            .values_list("supplier_code", flat=True)
            .distinct()
        )
        supplier_codes = {str(c).strip() for c in raw_codes if c and str(c).strip()}
        if not supplier_codes:
            return False

        for code in supplier_codes:
            qm = QuotationMaster.objects.filter(inquiry_no=inq_no, supplier_code=code).first()
            st = int(qm.status) if qm is not None and qm.status is not None else None
            if st != 3:
                return False

        old_status = int(inq.status if inq.status is not None else 0)
        now = timezone.now()
        username = (str(actor_username).strip()[:20] if actor_username else None) or None
        inq.status = 5
        inq.update_time = now
        inq.update_datetime = now
        if username:
            inq.update_user = username
        inq.save(update_fields=["status", "update_time", "update_user", "update_datetime"])
        qn = (quotation_no or "-").strip()[:20] or "-"
        qm_submit = (
            QuotationMaster.objects.filter(inquiry_no=inq_no, quotation_no=qn).first()
            if qn != "-"
            else None
        )
        submitter_name = (getattr(qm_submit, "supplier_name", None) or "").strip() or "—"
        RFQOperationLogs.try_append(
            inquiry_no=inq.inquiry_no,
            purchase_type=int(inq.purchase_type),
            operation_type=6,
            operation_user=username,
            quotation_no=qn,
            per_status=old_status,
            cur_status=5,
            operation_desc=f"供应商（{submitter_name}）提交报价，受邀供应商均提交报价，询价单报价结束",
        )
        try:
            from apps.pisadmin.basicinfo.views.email_utils import send_quote_ended_notice_to_purchaser

            send_quote_ended_notice_to_purchaser(inq, last_quotation_no=qn)
        except Exception:
            logger.exception("报价结束通知邮件发送失败")
        return True


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
        db_table = table_prefix + "misc_proc_inquiry_supplier"
        verbose_name = "杂采询价单-供应商关联表"
        verbose_name_plural = verbose_name
        unique_together = ("inquiry_no", "part_id", "supplier_code")
        ordering = ("id",)

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return self.supplier_name


class InquiryAttachment(models.Model):
    """杂采询价单-附件关联表（采购方上传）。发布询价生成报价单时不写入 `pissupplier.QuotationAttachment`，供应商通过详情中的询价附件只读展示。"""
    
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
        db_table = table_prefix + "misc_proc_inquiry_attachment"
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
    create_time = models.DateTimeField(db_column="createtime", auto_now_add=True, verbose_name="创建时间")
    create_user = models.CharField(max_length=20, db_column="createuser", null=True, blank=True, verbose_name="创建人")

    class Meta:
        db_table = table_prefix + "misc_proc_inquiry_material_cost"
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
        db_table = table_prefix + "misc_proc_inquiry_process_cost"
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
        db_table = table_prefix + "misc_proc_inquiry_other_cost"
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
        db_table = table_prefix + "misc_proc_inquiry_profit_cost"
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


class MiscLowPriceHeader(CoreModel):
    """比价-制程最低价记录主表。按询价单上阶物料料号分套；材料一行（最低重量×最低单价×数量）、加工一行（各报价单加工费合计之最小值）；包装费/运输费/利润率各一行。"""

    # 成本类别: 1-材料; 2-加工; 3-包装费; 4-运输费; 5-管销研费用(杂采制程最低价不落库); 6-利润率
    COST_TYPE_CHOICES = (
        ("1", "材料"),
        ("2", "加工"),
        ("3", "包装费"),
        ("4", "运输费"),
        ("5", "管销研费用"),
        ("6", "利润率"),
    )

    inquiry_no = models.CharField(
        max_length=20,
        db_index=True,
        db_column="inquiry_no",
        verbose_name="询价单号",
        help_text="业务主键列之一；逻辑主键与 id 并存",
    )
    part_id = models.CharField(max_length=50, db_column="PartId", verbose_name="产品料号")
    # 来源单号（报价单号/厂区等）；材料行可聚合多来源（如 W:单号;U:单号）；设计库字段名为 SouceNo
    souce_no = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        db_column="SouceNo",
        verbose_name="来源单号(报价单&询价单)",
    )
    cost_type = models.CharField(
        max_length=50,
        choices=COST_TYPE_CHOICES,
        db_column="CostType",
        verbose_name="成本类别",
    )
    item_no = models.CharField(
        max_length=100,
        db_column="ItemNo",
        verbose_name="项次名",
        help_text="根据成本类别获取询价单对应子表数据行，材料类别 - 材料成本的产品料号 part_id, 加工类别 - 加工工站 process_station",
    )
    min_price = models.CharField(
        max_length=10,
        db_column="MinPrice",
        verbose_name="最低价格",
        help_text="表结构为 varchar，若需参与运算可在业务层转换",
    )

    class Meta:
        db_table = table_prefix + "misc_low_price_header"
        verbose_name = "比价-制程最低价记录主表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime", "id")
        indexes = [
            models.Index(fields=["inquiry_no", "part_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.inquiry_no}-{self.part_id}-{self.cost_type}"


class MiscLowPriceDetail(CoreModel):
    """比价-制程最低价记录次表（材料：全供应商最低重量、最低单价各一行，material_spec 占位「-」）"""

    ITEM_NO_CHOICES = (
        ("1", "重量"),
        ("2", "单价"),
    )
    inquiry_no = models.CharField(max_length=20, db_column="inquiry_no", db_index=True, verbose_name="询价单号")
    part_id = models.CharField(max_length=50, db_column="PartId", verbose_name="产品料号")
    cost_type = models.CharField(
        max_length=50,
        db_column="CostType",
        verbose_name="成本类别",
        help_text="仅支持1-材料",
    )
    material_spec = models.CharField(max_length=50, db_column="materialspec", verbose_name="材料规格")
    item_no = models.CharField(
        max_length=100,
        db_column="ItemNo",
        verbose_name="项次名",
        help_text="策采：重量、损耗、单价；杂采：重量、单价",
        choices=ITEM_NO_CHOICES,
    )
    value = models.CharField(max_length=10, db_column="Value", verbose_name="最小值")
    souce_no = models.CharField(
        max_length=200,
        db_column="SouceNo",
        verbose_name="来源单号(报价单号或交易厂区)",
        help_text="重量/单价取最小值时对应报价单单号；单价来自杂采材料信息时存交易厂区代码",
    )

    class Meta:
        db_table = table_prefix + "misc_low_price_detail"
        verbose_name = "比价-制程最低价记录次表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime", "id")
        indexes = [
            models.Index(fields=["inquiry_no", "part_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.inquiry_no}-{self.part_id}-{self.item_no}"


class MiscNegotiationRecords(CoreModel):
    """杂采议价记录表"""

    inquiry_no = models.CharField(max_length=20, db_column="inquiry_no", db_index=True, verbose_name="询价单号")
    part_id = models.CharField(max_length=50, db_column="PartId", verbose_name="产品料号")
    supplier_code = models.CharField(max_length=50, null=True, blank=True, db_column="SupplierCode", verbose_name="供应商代码")
    bargaining_price = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, default=0, verbose_name="议价后价格")
    bargaining_time = models.DateTimeField(null=True, blank=True, verbose_name="议价时间")
    bargaining_user = models.CharField(max_length=20, null=True, blank=True, db_column="BargainingUser", verbose_name="议价人")
    is_awarded = models.IntegerField(default=0, null=True, blank=True, verbose_name="是否中标", help_text="是否中标(1:是 0:否)")
    quotation_no = models.CharField(max_length=20, null=True, blank=True, db_column="QuotationNo", verbose_name="报价单号")
    total_price_excl_tax = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, default=0, verbose_name="议价前不含税总价")
    total_price_incl_tax = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True, default=0, verbose_name="议价前含税总价")

    class Meta:
        db_table = table_prefix + "misc_negotiation_records"
        verbose_name = "杂采议价记录表"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime", "id")
        indexes = [
            models.Index(fields=["inquiry_no", "part_id"]),
            models.Index(
                fields=["inquiry_no", "part_id", "quotation_no"],
                name="pis_misc_ne_inq_part_qtn_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.inquiry_no}-{self.part_id}-{self.quotation_no or self.supplier_code}"


class RFQOperationLogs(CoreModel):
    """询价单操作日志表。

    按询价单号拉取全部记录：采购端 ``InquiryViewSet.operation_logs``（
    ``GET .../inquiry/{pk}/operation_logs/``）。
    """

    # (01询价单创;02询价单确认;03询价单发布;04询价单还原;05询价发送通知;06报价;07比议价;08议价审核提交;09议价审核完成;10议价审核驳回)
    OPERATION_TYPE_CHOICES = (
        (1, "询价单创建"),
        (2, "询价单确认"),
        (3, "询价单发布"),
        (4, "询价单还原"),
        (5, "报价截止"),
        (6, "供应商报价"),
        (7, "比议价"),
        (8, "议价审核提交"),
        (9, "议价审核完成"),
        (10, "议价审核驳回"),
    )
    PURCHASE_TYPE_CHOICES = (
        (1, "策采"),
        (2, "杂采"),
    )

    operation_type = models.CharField(max_length=20, db_column="OperationType", verbose_name="操作类型", choices=OPERATION_TYPE_CHOICES)
    operation_user = models.CharField(max_length=20, null=True, blank=True, db_column="OperationUser", verbose_name="操作人")
    operation_time = models.DateTimeField(null=True, blank=True, db_column="OperationTime", verbose_name="操作时间")
    operation_desc = models.TextField(max_length=200, null=True, blank=True, db_column="OperationDesc", verbose_name="操作描述")
    inquiry_no = models.CharField(max_length=20, db_column="InquiryNo", db_index=True, verbose_name="询价单号")
    quotation_no = models.CharField(max_length=20, null=False, blank=False, db_column="QuotationNo", db_index=True, verbose_name="报价单号")
    per_status = models.CharField(max_length=50, null=True, blank=True, db_column="PerStatus", verbose_name="作业前状态")
    cur_status = models.TextField(max_length=100, null=True, blank=True, db_column="CurStatus", verbose_name="作业后状态")
    is_show_user = models.IntegerField(null=True, blank=True, db_column="IsShowUser", verbose_name="履历显示否", help_text="履历显示否(1:是 0:否)")
    purchase_type = models.IntegerField(choices=PURCHASE_TYPE_CHOICES, null=False, blank=False, db_column="PurchaseType", verbose_name="采购类别", help_text="采购类别(1:策采 2:杂采)")

    class Meta:
        db_table = table_prefix + "rfq_operation_logs"
        verbose_name = "询价单操作日志"
        verbose_name_plural = verbose_name
        ordering = ("-create_datetime", "id")
        indexes = [
            models.Index(fields=["inquiry_no", "quotation_no"]),
        ]

    @classmethod
    def inquiry_status_display(cls, code: Optional[int]) -> str:
        """询价单状态码 → 与 Inquiry.STATUS_CHOICES 一致的可读文案。"""
        if code is None:
            return ""
        try:
            c = int(code)
        except (TypeError, ValueError):
            return str(code)
        return dict(Inquiry.STATUS_CHOICES).get(c, str(c))

    @classmethod
    def append(
        cls,
        *,
        inquiry_no: str,
        purchase_type: int,
        operation_type: int,
        operation_user: Optional[str] = None,
        quotation_no: Optional[str] = None,
        per_status: Optional[int] = None,
        cur_status: Optional[int] = None,
        operation_desc: Optional[str] = None,
        is_show_user: int = 1,
    ) -> None:
        """
        写入一条询价操作日志。quotation_no 无关联报价单时使用 \"-\"。
        operation_type 与 OPERATION_TYPE_CHOICES 取值 1–10 一致。
        """
        qn = (quotation_no or "-").strip()[:20] or "-"
        op_user = (operation_user or "").strip()[:20] if operation_user else None
        now = timezone.now()
        per_str = cls.inquiry_status_display(per_status) if per_status is not None else None
        cur_str = cls.inquiry_status_display(cur_status) if cur_status is not None else None
        desc = (operation_desc or "").strip()[:200] if operation_desc else None

        cls.objects.create(
            operation_type=str(int(operation_type)),
            operation_user=op_user,
            operation_time=now,
            operation_desc=desc,
            inquiry_no=(inquiry_no or "")[:20],
            quotation_no=qn,
            per_status=(per_str[:50] if per_str else None),
            cur_status=(cur_str[:100] if cur_str else None),
            is_show_user=is_show_user,
            purchase_type=int(purchase_type),
        )

    @classmethod
    def try_append(cls, **kwargs) -> None:
        """写入失败不影响主流程，仅记录异常日志。"""
        try:
            cls.append(**kwargs)
        except Exception:
            logger.exception("写入询价操作日志失败")

    def __str__(self) -> str:
        return f"{self.inquiry_no}-{self.quotation_no}"
