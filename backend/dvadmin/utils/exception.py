# -*- coding: utf-8 -*-

"""
@author: 猿小天
@contact: QQ:1638245306
@Created on: 2021/6/2 002 16:06
@Remark: 自定义异常处理
"""
import logging
import traceback

from django.db.models import ProtectedError
from django.http import Http404
from rest_framework.exceptions import APIException as DRFAPIException, AuthenticationFailed, NotAuthenticated
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.views import set_rollback, exception_handler

from dvadmin.utils.json_response import ErrorResponse

logger = logging.getLogger(__name__)


def _format_drf_detail(detail):
    """
    将 DRF ValidationError.detail 转为可读字符串。
    避免嵌套列表（如 items 多行明细）在简单拼接时只剩「items:{}」等无效提示。
    """
    if detail is None:
        return ""
    if isinstance(detail, dict):
        if not detail:
            return ""
        parts = []
        for k, v in detail.items():
            if isinstance(v, (list, tuple)):
                subs = []
                for item in v:
                    if isinstance(item, dict):
                        inner = _format_drf_detail(item)
                        if inner:
                            subs.append(inner)
                    else:
                        subs.append(str(item))
                if subs:
                    parts.append("%s: %s" % (k, "；".join(subs)))
            elif isinstance(v, dict):
                inner = _format_drf_detail(v)
                if inner:
                    parts.append("%s: %s" % (k, inner))
            else:
                parts.append("%s: %s" % (k, v))
        return "；".join(parts)
    if isinstance(detail, (list, tuple)):
        subs = []
        for item in detail:
            if isinstance(item, dict):
                inner = _format_drf_detail(item)
                if inner:
                    subs.append(inner)
            else:
                subs.append(str(item))
        return "；".join(subs)
    return str(detail)


class CustomAuthenticationFailed(NotAuthenticated):
    # 设置 status_code 属性为 400
    status_code = 400

def CustomExceptionHandler(ex, context):
    """
    统一异常拦截处理
    目的:(1)取消所有的500异常响应,统一响应为标准错误返回
        (2)准确显示错误信息
    :param ex:
    :param context:
    :return:
    """
    msg = ''
    code = 4000
    # 调用默认的异常处理函数
    response = exception_handler(ex, context)
    if isinstance(ex, AuthenticationFailed):
        # 如果是身份验证错误
        if response and response.data.get('detail') == "Given token not valid for any token type":
            code = 401
            msg = ex.detail
        elif response and response.data.get('detail') == "Token is blacklisted":
            # token在黑名单
            return ErrorResponse(status=HTTP_401_UNAUTHORIZED)
        else:
            code = 401
            msg = ex.detail
    elif isinstance(ex,Http404):
        code = 400
        msg = "接口地址不正确"
    elif isinstance(ex, DRFAPIException):
        set_rollback()
        detail = ex.detail
        if isinstance(detail, dict):
            msg = _format_drf_detail(detail) or str(detail)
        elif isinstance(detail, (list, tuple)):
            msg = _format_drf_detail(detail) or str(detail)
        else:
            msg = str(detail)
    elif isinstance(ex, ProtectedError):
        set_rollback()
        msg = "删除失败:该条数据与其他数据有相关绑定"
    # elif isinstance(ex, DatabaseError):
    #     set_rollback()
    #     msg = "接口服务器异常,请联系管理员"
    elif isinstance(ex, Exception):
        logger.exception(traceback.format_exc())
        msg = str(ex)
    return ErrorResponse(msg=msg, code=code)
