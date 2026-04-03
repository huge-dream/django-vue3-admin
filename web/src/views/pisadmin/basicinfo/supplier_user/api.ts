import { request } from '/@/utils/service'

const apiPrefix = '/api/pisadmin/basicinfo/supplier_users/'

export const GetList = (params: any) => request({ url: apiPrefix, method: 'get', params })
export const AddObj = (data: any) => request({ url: apiPrefix, method: 'post', data })
export const UpdateObj = (data: any) => request({ url: apiPrefix + data.id + '/', method: 'put', data })
export const DelObj = (id: string | number) => request({ url: apiPrefix + id + '/', method: 'delete' })
