import { request } from "/@/utils/service";

export function getCaptcha() {
    return request({
        url: '/api/captcha/',
        method: 'get',
    });
}
export function login(params: object) {
    return request({
        url: '/api/login/',
        method: 'post',
        data: params
    });
}

export function loginChangePwd(data: object) {
    return request({
        url: '/api/system/user/login_change_password/',
        method: 'post',
        data: data
    });
}

export function getUserInfo() {
    return request({
        url: '/api/system/user/user_info/',
        method: 'get',
    });
}

export function register(params: object) {
    return request({
        url: '/api/register/',
        method: 'post',
        data: params
    });
}