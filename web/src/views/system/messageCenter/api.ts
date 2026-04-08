import {request} from '/@/utils/service';
import {PageQuery, AddReq, DelReq, EditReq, InfoReq} from '@fast-crud/fast-crud';

export const apiPrefix = '/api/system/message_center/';

export function GetList(query: PageQuery) {
    return request({
        url: apiPrefix,
        method: 'get',
        params: query,
    });
}

export function GetObj(id: InfoReq) {
    return request({
        url: apiPrefix + id + '/',
        method: 'get',
    });
}

/**
 * 获取自己接收的消息
 * @param query
 * @returns {*}
 * @constructor
 */
export function GetSelfReceive (query:PageQuery) {
    return request({
        url: apiPrefix + 'get_self_receive/',
        method: 'get',
        params: query
    })
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
        data: {id},
    });
}
