import permissionDirective from './directive.permission'
import permissionFunc from './func.permission'
export const RegisterPermission = function (app:any) {
  app.directive('permission', permissionDirective)
  app.provide('$hasPermissions',permissionFunc.hasPermissions)
}
