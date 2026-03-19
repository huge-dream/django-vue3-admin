import { request } from '/@/utils/service'

const baseUrl = '/api/procurement/inquiry/'

export const GetList = (params: any) => request({ url: baseUrl, method: 'get', params })
export const GetObj = (id: string | number) => request({ url: baseUrl + id + '/', method: 'get' })
export const AddObj = (data: any) => request({ url: baseUrl, method: 'post', data })
export const UpdateObj = (data: any) => request({ url: baseUrl + data.id + '/', method: 'put', data })
export const DelObj = (id: string | number) => request({ url: baseUrl + id + '/', method: 'delete' })
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
