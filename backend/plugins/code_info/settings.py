from application import settings

# ================================================= #
# ***************** 插件配置区开始 *******************
# ================================================= #
# 路由配置
plugins_url_patterns = [
    {"re_path": r'api/code_info/', "include": "code_info.urls"},
]
# app 配置
apps = ['code_info']
# 租户模式中，public模式共享app配置
tenant_shared_apps = ['code_info']
# ================================================= #
# ******************* 插件配置区结束 *****************
# ================================================= #

# ********** 赋值到 settings 中 **********
settings.INSTALLED_APPS += [app for app in apps if app not in settings.INSTALLED_APPS]
settings.TENANT_SHARED_APPS += tenant_shared_apps
# ********** 注册路由 **********
settings.PLUGINS_URL_PATTERNS += plugins_url_patterns
