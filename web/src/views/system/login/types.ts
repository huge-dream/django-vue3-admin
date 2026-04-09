export interface OAuth2Backend {
  app_name:  string;
  backend_name: string;
  icon: string;
  authentication_url: string;
}

/** JWT 登录成功 data.role_info 单项（与后端 Users.role 一致） */
export interface LoginRoleInfo {
  id: number;
  name: string;
  key: string;
}

