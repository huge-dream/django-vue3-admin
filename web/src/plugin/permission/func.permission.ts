import XEUtils from 'xe-utils'
import {BtnPermissionStore} from "/@/plugin/permission/store.permission";

export default {
  hasPermissions (value:string | string[]) {
    const BtnPermission = BtnPermissionStore().data
    if (import.meta.env.VITE_PM_ENABLED) {
      if(value instanceof Array){
        return XEUtils.includeArrays(BtnPermission, value)
      }else if(typeof value === 'string'){
        const index = XEUtils.arrayIndexOf(BtnPermission, value)
        return index>-1?true:false
      }
     }
    return true
  }
}
