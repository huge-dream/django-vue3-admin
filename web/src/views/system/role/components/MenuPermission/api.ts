import { request } from "/@/utils/service";
import XEUtils from 'xe-utils';
/**
 * 获取菜单树
 * @param roleId
 * @param query
 */
export function getMenuPremissionTree(query:object) {
  return request({
    url: '/api/system/role_menu_permission/menu_permission_tree/',
    method: 'get',
    params:query
  }).then((res:any)=>{
    return  XEUtils.toArrayTree(res.data,{ parentKey: 'parent_id', key: 'id', children: 'children',})
  })
}

/**
 * 获取已授权的菜单
 * @param query
 */
export function getMenuPremissionChecked(query:object) {
  return request({
    url: '/api/system/role_menu_permission/get_menu_permission_checked/',
    method: 'get',
    params:query
  }).then((res:any)=>{
    return res.data
  })
}


/**
 * 保存菜单权限
 */
export function saveMenuPremission(data:object) {
  return request({
    url:'/api/system/role_menu_permission/save_menu_permission/',
    method:'post',
    data
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

