import permissionUtil from './func.permission'
export default {
  mounted (el:any, binding:any) {
    const { value } = binding
    const hasPermission = permissionUtil.hasPermissions(value)
    if (!hasPermission) {
      el.parentNode && el.parentNode.removeChild(el)
    }
  }
}
