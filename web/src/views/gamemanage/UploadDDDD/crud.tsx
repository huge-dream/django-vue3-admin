// 将文件传到后端
import * as api from './api'
import {auth} from '/@/utils/authFunction'

export const UploadDDDD = async (obj: any) => {
    return await api.UploadDDDD(obj);
}
