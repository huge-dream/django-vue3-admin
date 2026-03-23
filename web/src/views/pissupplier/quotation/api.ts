import { request } from '/@/utils/service'

/**
 * 与后端路由一致：
 * - application/urls.py → path("api/pissupplier/", include("apps.pissupplier.urls"))
 * - apps/pissupplier/urls.py → router.register 资源名（下划线）
 *
 * 完整路径示例：GET /api/pissupplier/quotation_master/
 */
export const PISSUPPLIER_API_PREFIX = '/api/pissupplier/'

/** 与 apps.pissupplier.urls 中 router.register 一一对应（供扩展子资源调用） */
export const PISSUPPLIER_ROUTES = {
  quotation_master: `${PISSUPPLIER_API_PREFIX}quotation_master/`,
  quotation_attachment: `${PISSUPPLIER_API_PREFIX}quotation_attachment/`,
  quotation_material: `${PISSUPPLIER_API_PREFIX}quotation_material/`,
  quotation_process: `${PISSUPPLIER_API_PREFIX}quotation_process/`,
  quotation_other: `${PISSUPPLIER_API_PREFIX}quotation_other/`,
  quotation_profit: `${PISSUPPLIER_API_PREFIX}quotation_profit/`,
  quotation_item: `${PISSUPPLIER_API_PREFIX}quotation_item/`
} as const

const baseUrl = PISSUPPLIER_ROUTES.quotation_master

export type QuotationStatusCode = 1 | 2 | 3
export type PaymentCode = 1 | 2 | 3 | 4

/**
 * 列表：GET quotation_master/；详情/更新：pk 对应模型主键 autoid
 *
 * 报价主表（QuotationMaster）仅含 inquiry_no，不含询价名称与询价模板编号；列表展示由 crud 中
 * 关联 Inquiry 与成本/价格模板接口补全 title、template 与模板名称。
 *
 * 更新（PUT）在弹窗「保存」时调用，不改变 status / quotetime；正式提交走 POST `{id}/submit/`。
 * 更新（PUT）时序列化要求 supplier_code / supplier_name 等字段；前端从列表/详情映射 supplierCode 并在保存时写回。
 * 成本结构须提交 material_costs、process_costs、other_costs、profit_costs（与 QuotationMasterCreateUpdateSerializer），
 * 勿使用 cost_items——后端不识别，子表不会更新。
 */
export const getList = (params: any) => request({ url: baseUrl, method: 'get', params })
export const getDetail = (id: string | number) => request({ url: `${baseUrl}${id}/`, method: 'get' })
export const create = (data: any) => request({ url: baseUrl, method: 'post', data })
export const update = (id: string | number, data: any) => request({ url: `${baseUrl}${id}/`, method: 'put', data })

export const submit = (id: string | number, data: any) => request({ url: `${baseUrl}${id}/`, method: 'put', data })

/** 正式提交报价：写入 quotetime、status=2 */
export const submitOfficial = (id: string | number) =>
  request({ url: `${baseUrl}${id}/submit/`, method: 'post', data: {} })
