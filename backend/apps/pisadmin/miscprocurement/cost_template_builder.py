"""
成本结构模板构建工具

负责将前端发送的分层结构化 sections 数据展开并逐条持久化到数据库。

数据流：
  前端 SectionBuilder 发送 → sections 数组
  ├─ section 1 (title: "材料成本")
  │  └─ fields 数组
  │     ├─ field 1 (key: "material", nameCn: "材质")
  │     ├─ field 2 (key: "length", nameCn: "长")
  │     └─ field 3 (key: "unitPrice", nameCn: "单价")
  ├─ section 2 (title: "加工成本")
  │  └─ fields 数组
  │     ├─ field 1 (key: "process_station", nameCn: "加工工站")
  │     └─ field 2 (key: "process_price", nameCn: "加工费")
  └─ section 3 (title: "利润")
     └─ fields 数组
        └─ field 1 (key: "profit_rate", nameCn: "利润率")

本工具将上述结构展开为 CostEstimateTemplateBody 表的独立行：
  item_order: 全局行号（1, 2, 3, ..., 6）
  item_no: 字段 key（material, length, unitPrice, ...）
  item_name_cn: 字段中文名称（材质, 长, 单价, ...）
  item_name_en: 字段英文名称
  item_name_vn: 字段越南名称
  cost_category: section 对应的成本类别（1=材料成本, 2=加工成本, 5=利润, ...）
  is_fixed: 字段是否固定（1=固定, 0=变量）
  is_computed: 是否自动计算（1=是, 0=否）
  purchaser_required: 采购人是否必填（1=是, 0=否）
  supplier_required: 供应商操作（0-6）
  remark: 字段备注

说明：独立成本模板在 PIS 中「新版本」派生使用 serializers.create_cost_template_new_version（同 template_no、
version 递增；若提交明细与源版本规范化后一致则拒绝创建）；确认新版本时由 CostEstimateTemplateViewSet.confirm
将同编号更低版本主表行置为作废(2)。本模块将前端 sections 展开后写入 `CostEstimateTemplateBody`。
"""

from typing import Dict, List, Optional, Tuple
from django.utils import timezone
from apps.pisadmin.miscprocurement.models import CostEstimateTemplateHead, CostEstimateTemplateBody


class CostTemplateBuilder:
    """成本模板构建器：负责将前端sections数据展开持久化到数据库"""

    SUPPLIER_BEHAVIOR_TO_CODE = {
        "prefill_locked": 1,
        "prefill_editable": 2,
        "hidden_required": 3,
        "hidden_optional": 4,
        "required": 5,
        "optional": 6,
    }
    
    # Section title 与 cost_category 的映射表
    COST_CATEGORY_MAPPING = {
        "材料成本": "1",
        "加工成本": "2",
        "其它成本": "3",
        "其他成本": "3",
        "管销研费用": "4",
        "管销研": "4",
        "利润": "5",
        "税金": "6",
        "税费成本": "6",
        "产品明细": "7",
    }

    @classmethod
    def get_cost_category_from_title(cls, title: str) -> str:
        """
        根据 section 的 title 获取对应的 cost_category 代码
        
        Args:
            title: section 的标题（如 "材料成本"、"加工成本"）
            
        Returns:
            cost_category 代码（字符串，"1" 到 "7"）
        """
        return cls.COST_CATEGORY_MAPPING.get(title, "1")

    @classmethod
    def normalize_supplier_required(
        cls,
        value,
        purchaser_required: int = 0,
        supplier_editable=None,
        is_computed: int = 0,
    ) -> int:
        if is_computed:
            return 0
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return 0
            if text in cls.SUPPLIER_BEHAVIOR_TO_CODE:
                return cls.SUPPLIER_BEHAVIOR_TO_CODE[text]
            try:
                code = int(text)
                if 0 <= code <= 6:
                    return code
            except ValueError:
                pass
        elif isinstance(value, bool):
            if purchaser_required:
                if value:
                    return 2 if supplier_editable else 1
                return 4 if supplier_editable else 3
            return 5 if value else 6
        elif value is not None:
            try:
                code = int(value)
                if 0 <= code <= 6:
                    return code
            except (TypeError, ValueError):
                pass

        if purchaser_required:
            if supplier_editable is True:
                return 4
            if supplier_editable is False:
                return 3
        return 0

    @classmethod
    def normalize_purchaser_required(cls, value, is_computed: int = 0) -> int:
        if is_computed:
            return 0
        if value in (None, ""):
            return 0
        if isinstance(value, bool):
            return 1 if value else 0
        try:
            return 1 if int(value) else 0
        except (TypeError, ValueError):
            if isinstance(value, str):
                return 1 if value.strip().lower() in ("true", "yes", "y", "on") else 0
            return 0

    @classmethod
    def build_body_records_from_sections(
        cls,
        sections: Optional[List[Dict]]
    ) -> List[Tuple[Dict, str]]:
        """
        将前端发送的 sections 数据展开成 body 记录列表
        
        Args:
            sections: 前端发送的 sections 数据（来自 SectionBuilder）
            
        Returns:
            list of (record_dict, cost_category) 元组
            其中 record_dict 包含所有需要存储到 CostEstimateTemplateBody 的字段
        """
        if not sections:
            return []
        
        body_records = []
        global_item_order = 1  # 全局行号
        
        for section in sections:
            if not isinstance(section, dict):
                continue
            
            section_title = section.get("title") or section.get("name", "")
            cost_category = cls.get_cost_category_from_title(section_title)
            fields = section.get("fields", [])
            
            if not fields:
                # 旧格式兼容：section 本身是一个 item
                body_records.append((
                    {
                        "cost_category": section.get("cost_category", cost_category),
                        "item_order": section.get("item_order", global_item_order),
                        "item_no": section.get("item_no", str(global_item_order)),
                        "item_name_cn": section.get("item_name_cn", ""),
                        "item_name_en": section.get("item_name_en", ""),
                        "item_name_vn": section.get("item_name_vn", ""),
                        "is_fixed": int(section.get("is_fixed", section.get("item_category", 0)) or 0),
                        "is_computed": int(section.get("is_computed", 0) or 0),
                        "purchaser_required": cls.normalize_purchaser_required(
                            section.get("purchaser_required", 0),
                            is_computed=int(section.get("is_computed", 0) or 0),
                        ),
                        "supplier_required": cls.normalize_supplier_required(
                            section.get("supplier_required", section.get("supplier_behavior")),
                            purchaser_required=cls.normalize_purchaser_required(
                                section.get("purchaser_required", 0),
                                is_computed=int(section.get("is_computed", 0) or 0),
                            ),
                            supplier_editable=section.get("supplier_editable"),
                            is_computed=int(section.get("is_computed", 0) or 0),
                        ),
                        "remark": section.get("remark"),
                    },
                    cost_category
                ))
                global_item_order += 1
            else:
                # 新格式：迭代 section 中的 fields，逐条创建明细
                for field_idx, field in enumerate(fields, start=1):
                    if not isinstance(field, dict):
                        continue
                    
                    # ============ 提取字段信息 ============
                    field_key = field.get("key", "")
                    field_label = field.get("label", "")
                    field_name_cn = field.get("nameCn") or field_label or ""
                    field_name_en = field.get("nameEn", "")
                    field_name_vn = field.get("nameVn", "")
                    remark = field.get("remark", "")
                    
                    # ============ 判断字段属性 ============
                    # 自动计算：根据 autoFill 标志判断
                    is_computed = 1 if field.get("autoFill") else 0
                    
                    # 采购人必填
                    purchaser_required = cls.normalize_purchaser_required(field.get("purchaserRequired"), is_computed=is_computed)
                    
                    supplier_required = cls.normalize_supplier_required(
                        field.get("supplier_required", field.get("supplierBehavior")),
                        purchaser_required=purchaser_required,
                        supplier_editable=field.get("supplierEditable"),
                        is_computed=is_computed,
                    )
                    if supplier_required == 0 and "supplierRequired" in field:
                        supplier_required = cls.normalize_supplier_required(
                            field.get("supplierRequired"),
                            purchaser_required=purchaser_required,
                            supplier_editable=field.get("supplierEditable"),
                            is_computed=is_computed,
                        )
                    
                    # 固定字段：fixed=True 表示固定字段（is_fixed=1）
                    is_fixed = 1 if field.get("fixed") else 0
                    
                    # ============ 构建记录 ============
                    record = {
                        "cost_category": cost_category,
                        "item_order": global_item_order,
                        "item_no": field_key or str(field_idx),
                        "item_name_cn": field_name_cn,
                        "item_name_en": field_name_en,
                        "item_name_vn": field_name_vn,
                        "is_fixed": is_fixed,
                        "is_computed": is_computed,
                        "purchaser_required": purchaser_required,
                        "supplier_required": supplier_required,
                        "remark": remark,
                    }
                    
                    body_records.append((record, cost_category))
                    global_item_order += 1
        
        return body_records

    @classmethod
    def create_cost_template_body_records(
        cls,
        template_head: CostEstimateTemplateHead,
        sections: Optional[List[Dict]],
        create_user: Optional[str] = None,
        create_time: Optional[object] = None
    ) -> int:
        """
        根据 sections 数据逐条创建成本模板明细（body 记录）
        
        Args:
            template_head: 成本模板主表记录
            sections: 前端发送的 sections 数据
            create_user: 创建人用户名（可选，如果为None则不设置）
            create_time: 创建时间（可选，如果为None则使用当前时间）
            
        Returns:
            创建的记录数
        """
        body_records = cls.build_body_records_from_sections(sections)
        
        if not body_records:
            return 0
        
        # 如果未提供，使用当前时间
        if create_time is None:
            create_time = timezone.now()
        
        # 批量创建 body 记录
        head_ver = getattr(template_head, "version", None)
        if head_ver is None:
            head_ver = 1
        bulk_objects = [
            CostEstimateTemplateBody(
                template_no=template_head.template_no,
                version=head_ver,
                create_user=create_user,
                create_time=create_time,
                update_user=create_user,
                update_time=create_time,
                **record_dict
            )
            for record_dict, _ in body_records
        ]
        
        created_records = CostEstimateTemplateBody.objects.bulk_create(bulk_objects)
        return len(created_records)

    @classmethod
    def debug_print_sections_expansion(
        cls,
        sections: Optional[List[Dict]]
    ) -> None:
        """
        调试函数：打印 sections 展开过程
        用于验证数据转换逻辑是否正确
        """
        if not sections:
            print("❌ sections 为空")
            return
        
        body_records = cls.build_body_records_from_sections(sections)
        
        print(f"\n📊 sections 展开结果：共 {len(body_records)} 条明细")
        print("=" * 100)
        
        for idx, (record, cost_category) in enumerate(body_records, start=1):
            cost_category_display = cls.COST_CATEGORY_MAPPING.get(
                [k for k, v in cls.COST_CATEGORY_MAPPING.items() if v == cost_category][0] if any(
                    k for k, v in cls.COST_CATEGORY_MAPPING.items() if v == cost_category
                ) else "unknown",
                "未知"
            )
            
            print(f"\n[条目 {idx}] 项次序号: {record['item_order']}")
            print(f"  成本类别: {record['cost_category']} ({cost_category_display})")
            print(f"  项号: {record['item_no']}")
            print(f"  中文名: {record['item_name_cn']}")
            print(f"  英文名: {record['item_name_en']}")
            print(f"  越南名: {record['item_name_vn']}")
            print(f"  固定字段: {record['is_fixed']} {'✓' if record['is_fixed'] else '✗'}")
            print(f"  自动计算: {record['is_computed']} {'✓' if record['is_computed'] else '✗'}")
            print(f"  采购必填: {record['purchaser_required']} {'✓' if record['purchaser_required'] else '✗'}")
            print(f"  供应商操作: {record['supplier_required']}")
            print(f"  备注: {record['remark']}")
        
        print("\n" + "=" * 100)
