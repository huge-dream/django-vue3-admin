import { request } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';
import XEUtils from 'xe-utils';

export const apiPrefix = '/api/system/dictionary/';
export function GetList(query: PageQuery) {
    return request({
        url: apiPrefix,
        method: 'get',
        params: query,
    })
}
export function GetObj(id: InfoReq) {
    return request({
        url: apiPrefix + id,
        method: 'get',
    });
}

export function AddObj(obj: AddReq) {
    return request({
        url: apiPrefix,
        method: 'post',
        data: obj,
    });
}

export function UpdateObj(obj: EditReq) {
    return request({
        url: apiPrefix + obj.id + '/',
        method: 'put',
        data: obj,
    });
}

export function DelObj(id: DelReq) {
    return request({
        url: apiPrefix + id + '/',
        method: 'delete',
        data: { id },
    });
}
