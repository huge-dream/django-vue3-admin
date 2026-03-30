import { request } from '/@/utils/service'

const baseUrl = '/api/pisadmin/miscprocurement/inquiry/'

export const GetList = (params: any) => request({ url: baseUrl, method: 'get', params })
export const GetObj = (id: string | number) => request({ url: baseUrl + id + '/', method: 'get' })
export const AddObj = (data: any) => request({ url: baseUrl, method: 'post', data })
export const UpdateObj = (data: any) => request({ url: baseUrl + data.id + '/', method: 'put', data })
export const DelObj = (id: string | number) => request({ url: baseUrl + id + '/', method: 'delete' })
export const ConfirmObj = (id: string | number) => request({ url: `${baseUrl}${id}/confirm/`, method: 'put' })
export const RestoreObj = (id: string | number) => request({ url: `${baseUrl}${id}/restore/`, method: 'put' })
export const PublishObj = (id: string | number) => request({ url: `${baseUrl}${id}/publish/`, method: 'put' })
export const StartBargainingObj = (id: string | number) => request({ url: `${baseUrl}${id}/start_bargaining/`, method: 'put' })
/** 确认比价：料号由后端从上阶物料表解析 */
export const ConfirmNegotiationObj = (id: string | number, data?: Record<string, unknown>) =>
  request({ url: `${baseUrl}${id}/confirm_negotiation/`, method: 'put', data: data ?? {} })
export const SubmitPriceAuditObj = (id: string | number) => request({ url: `${baseUrl}${id}/submit_price_audit/`, method: 'put' })
/** 查询杂采议价记录（比价议价价格存此表，非报价明细「中标价格」） */
export const GetNegotiationRecordsObj = (id: string | number, params?: { part_id?: string }) =>
  request({ url: `${baseUrl}${id}/negotiation_records/`, method: 'get', params: params ?? {} })
/** 保存比价中的议价后价格、中标否至杂采议价记录表 */
export const SaveNegotiationRecordsObj = (
  id: string | number,
  data: {
    part_id?: string
    records: {
      quotation_no: string
      supplier_code?: string
      is_awarded: number
      bargaining_price: number | null
      total_price_excl_tax?: number | null
      total_price_incl_tax?: number | null
    }[]
  }
) => request({ url: `${baseUrl}${id}/save_negotiation_records/`, method: 'put', data })
export const UploadFile = (data: FormData) =>
  request({
    url: '/api/system/file/',
    method: 'post',
    data,
    timeout: 60000,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
