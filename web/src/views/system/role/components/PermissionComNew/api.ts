import { request } from "/@/utils/service";
import XEUtils from "xe-utils";
/**
 * 获取角色的授权列表
 * @param roleId
 * @param query
 */
export function getRolePermission(query:object) {
  return request({
    url: '/api/system/role_menu_button_permission/get_role_permission/',
    method: 'get',
    params:query
  }).then((res:any)=>{
    return XEUtils.toArrayTree(res.data, {key: 'id', parentKey: 'parent',children: 'children',strict: false})
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

export function getDataPermissionRange(query:object) {
  return request({
    url: '/api/system/role_menu_button_permission/data_scope/',
    method: 'get',
    params:query
  })
}

export function getDataPermissionRangeAll() {
  return request({
    url: '/api/system/role_menu_button_permission/data_scope/',
    method: 'get',
  })
}
export function getDataPermissionDept(query:object) {
  return request({
    url: '/api/system/role_menu_button_permission/role_to_dept_all/',
    method: 'get',
    params:query
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

