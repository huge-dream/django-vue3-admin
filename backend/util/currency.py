from uuid import uuid4
from datetime import datetime

from django.db import connection
from django.db.models import  Model
from django.core.cache import cache


def create_code(model,prefix):
    current_date = datetime.now().strftime('%Y%m%d%H%M%S')
    code = f"{prefix}{current_date}" + str(uuid4().int)[:6]
    return code

def lock(key):
    if callable(key):  # @lock
        def inner(*args, **kwargs):
            with cache.lock(key='lock'):
                return key(*args, **kwargs)
        inner.__name__ = key.__name__
    else:  # @lock(key='aaa')
        def inner(func):
            def _inner(*args, **kwargs):
                with cache.lock(key=key):
                    return func(*args, **kwargs)
            _inner.__name__ = func.__name__
            return _inner
    return inner

def recursion_down_fast(instance:Model, parent='parent', key='id') -> list[int]:
    """向下递归instance的所有子级，且返回一维列表，使用sql优化，速度非常快"""
    if not instance:
        return []
    sql = f"""
    WITH RECURSIVE children AS (
        SELECT id, {key} AS param_{key} FROM {instance.__class__._meta.db_table} WHERE {parent}_id = %s UNION ALL
        SELECT a.id, a.{key} AS param_{key} FROM {instance.__class__._meta.db_table} a
        INNER JOIN children b ON a.{parent}_id = b.id
    ) SELECT param_{key} FROM children;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [getattr(instance, key)])
        data = cursor.fetchall()
        return [getattr(instance, key), *[i[0] for i in data]]

def recursion_up_fast(instance: Model, parent='parent', key='id') -> list[int]:
    """向上递归instance的所有父级，使用sql优化，速度非常快"""
    if not instance:
        return []
    sql = f"""
    WITH RECURSIVE parents AS (
        SELECT id, {key} as param_{key}, {parent}_id FROM {instance.__class__._meta.db_table} WHERE id = %s UNION ALL
        SELECT a.id, a.{key} as param_{key}, a.{parent}_id FROM {instance.__class__._meta.db_table} a
        INNER JOIN parents b ON a.id = b.{parent}_id
    ) SELECT param_{key} FROM parents;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [getattr(instance, key)])
        data = cursor.fetchall()
        return [getattr(instance, key), *[i[0] for i in data]]

def recursion_up_joint(instance: Model, parent='parent', key='name', joint='/') -> str:
    """向上递归instance所有父级并拼接需要的值，返回完整路径，使用sql优化，速度非常快"""
    if instance is None:
        return ''
    sql = f"""
    WITH RECURSIVE parents AS (
        SELECT id, {parent}_id, {key}::TEXT AS path FROM {instance.__class__._meta.db_table} WHERE {key} = %s AND id = %s UNION ALL
        SELECT a.id, a.{parent}_id, (a.{key} || '{joint}' || b.path)::TEXT FROM {instance.__class__._meta.db_table} a
        INNER JOIN parents b ON a.id = b.{parent}_id
    ) SELECT path FROM parents where {parent}_id IS NULL;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [getattr(instance, key), instance.pk])
        data = cursor.fetchall()
        try:
            return data[0][0]
        except IndexError:
            raise Exception('找不到初始数据')