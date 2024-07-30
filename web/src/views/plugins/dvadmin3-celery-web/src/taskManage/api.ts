import {request} from '/@/utils/service';
import {UserPageQuery, AddReq, DelReq, EditReq, InfoReq} from '@fast-crud/fast-crud';

export const apiPrefix = '/api/dvadmin_celery/';

export function getIntervalScheduleList(query: UserPageQuery) {
    return request({
        url: apiPrefix + 'intervalschedule/',
        method: 'get',
        params: query,
    });
}

export function getCrontabScheduleList(query: UserPageQuery) {
    return request({
        url: apiPrefix + 'crontabschedule/',
        method: 'get',
        params: query,
    });
}

export function getBackendTaskList(query: UserPageQuery) {
    return request({
        url: apiPrefix + 'task/job_list/',
        method: 'get',
        params: query,
    });
}

export function getTaskList(query: UserPageQuery) {
    return request({
        url: apiPrefix + 'task/',
        method: 'get',
        params: query,
    });
}

export function GetTask(id: InfoReq) {
    return request({
        url: apiPrefix + id,
        method: 'get',
    });
}

export function AddTask(obj: AddReq) {
    return request({
        url: apiPrefix + 'task/',
        method: 'post',
        data: obj,
    });
}

export function EditTask(obj: AddReq) {
    return request({
        url: apiPrefix + 'task/' + obj.id + '/',
        method: 'put',
        data: obj,
    });
}

export function UpdateTask(obj: EditReq) {
    return request({
        url: apiPrefix + 'task/update_status/' + obj.id + '/',
        method: 'post',
        data: obj,
    });
}

export function RunTask(obj: AddReq) {
    return request({
        url: apiPrefix + 'task/run_task/' + obj.id + '/',
        method: 'post',
        data: obj,
    });
}

export function DelTask(obj: DelReq) {
    return request({
        url: apiPrefix + 'task/delete_task/' + obj.id + '/',
        method: 'delete',
        data: obj,
    });
}
