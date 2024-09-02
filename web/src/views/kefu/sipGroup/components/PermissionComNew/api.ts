import { request } from "/@/utils/service";

/**
 * 获取角色的授权列表
 * @param roleId
 * @param query
 */
export function getRolePremission(query:object) {
  return request({
    url: '/api/system/role_menu_button_permission/get_role_premission/',
    method: 'get',
    params:query
  })
}

/***
 * 设置角色的权限
 * @param roleId
 * @param data
 */
export function setRolePremission(roleId:any,data:object) {
  return request({
    url: `/api/system/role_menu_button_permission/${roleId}/set_role_premission/`,
    method: 'put',
    data
  })
}

export function getDataPermissionRange() {
  return request({
    url: '/api/system/role_menu_button_permission/data_scope/',
    method: 'get',
  })
}
export function getDataPermissionDept() {
  return request({
    url: '/api/system/role_menu_button_permission/role_to_dept_all/',
    method: 'get'
  })
}

export function getDataPermissionMenu() {
  return request({
    url: '/api/system/role_menu_button_permission/get_role_permissions/',
    method: 'get'
  })
}

/**
 * 设置按钮的数据范围
 */
export function setBtnDatarange(roleId:number,data:object) {
  return request({
    url: `/api/system/role_menu_button_permission/${roleId}/set_btn_datarange/`,
    method: 'put',
    data
  })
}

