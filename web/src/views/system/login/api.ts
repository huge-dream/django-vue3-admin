import { request } from "/@/utils/service";
import type { LoginRoleInfo } from "./types";

/** 与后端 login._is_supplier_portal_role_key 一致：供应商端允许的角色 key */
export function isSupplierPortalRoleKey(key: string | undefined | null): boolean {
	if (!key) return false;
	return key === "supplier" || key.startsWith("supplier_");
}

/** 账号是否仅有供应商端角色（此类账号仅允许走 /api/login/supplier/） */
export function isSupplierOnlyAccount(roleInfo: LoginRoleInfo[] | undefined | null): boolean {
	if (!roleInfo?.length) return false;
	return roleInfo.every((r) => isSupplierPortalRoleKey(r.key));
}

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

export function getBackends() {
    return request({
        url: '/api/dvadmin3_social_oauth2/backend/get_login_backend/',
        method: 'get',
    });
}

export function supplierLogin(params: object) {
    return request({
        url: '/api/login/supplier/',
        method: 'post',
        data: params
    });
}