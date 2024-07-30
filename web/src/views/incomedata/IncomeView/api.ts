import {request} from '/@/utils/service';

export const apiPrefix = 'api/incomedata/get_income/';

export function getIncome(obj: any) {
    if (obj == null) {
        return request({
            url: apiPrefix,
            method: 'get',
        });
    } else {
        return request({
            url: apiPrefix,
            method: 'post',
            data: obj,
        });
    }
}
