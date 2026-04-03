import { request } from '/@/utils/service'

const apiPrefix = '/api/pisadmin/basicinfo/supplier_users/'

export const GetList = (params: any) => request({ url: apiPrefix, method: 'get', params })
