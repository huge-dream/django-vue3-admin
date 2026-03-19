import { request } from '/@/utils/service'

const apiPrefix = '/api/system/currencies/'

export const GetList = (params: any) => request({ url: apiPrefix, method: 'get', params })
export const AddObj = (data: any) => request({ url: apiPrefix, method: 'post', data })
export const UpdateObj = (data: any) => request({ url: apiPrefix + data.id + '/', method: 'put', data })
export const DelObj = (id: string | number) => request({ url: apiPrefix + id + '/', method: 'delete' })

// 用于下拉选择交易厂区（公司代码）
export const GetCompanies = (params: any = { page: 1, pageSize: 200 }) =>
	request({ url: '/api/system/companies/', method: 'get', params })
