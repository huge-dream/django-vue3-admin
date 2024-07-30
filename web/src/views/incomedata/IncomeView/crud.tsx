import * as api from './api'

export const getIncome = async (obj: any = null) => {
    return await api.getIncome(obj);
}