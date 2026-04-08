import { request } from '/@/utils/service'
import { PageQuery, AddReq, EditReq, InfoReq } from '@fast-crud/fast-crud'

// 成本结构模板（独立表）：t_CostEstimate_Template_Head/Body
export const apiPrefix = '/api/pisadmin/miscprocurement/cost_template/'

export function GetList(query: PageQuery) {
  return request({
    url: apiPrefix,
    method: 'get',
    params: query
  })
}

export function GetObj(id: InfoReq) {
  return request({
    url: apiPrefix + id + '/',
    method: 'get'
  })
}

export function AddObj(obj: AddReq) {
  return request({
    url: apiPrefix,
    method: 'post',
    data: obj
  })
}

export function UpdateObj(obj: EditReq) {
  return request({
    url: apiPrefix + obj.id + '/',
    method: 'put',
    data: obj
  })
}

/** 未确认 → 已确认：POST /cost_template/{id}/confirm/ */
export function ConfirmObj(id: string | number) {
  return request({
    url: `${apiPrefix}${id}/confirm/`,
    method: 'post',
    data: {}
  })
}

/** 已确认模板派生新版本：POST /cost_template/{sourceId}/new_version/（同模板编号，服务端 version=max+1） */
export function NewVersionFromSource(sourceId: string | number, data: Record<string, unknown>) {
  return request({
    url: `${apiPrefix}${sourceId}/new_version/`,
    method: 'post',
    data
  })
}
