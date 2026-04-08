import { request } from '/@/utils/service'

const baseUrl = '/api/pisadmin/miscprocurement/rfq_operation_logs/'

export const GetList = (params: any) => request({ url: baseUrl, method: 'get', params })
