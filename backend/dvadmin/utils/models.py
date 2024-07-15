# -*- coding: utf-8 -*-

"""
@author: 猿小天
@contact: QQ:1638245306
@Created on: 2021/5/31 031 22:08
@Remark: 公共基础model类
"""
from datetime import datetime
from importlib import import_module

from application import settings
from django.apps import apps
from django.conf import settings
from django.db import models
from rest_framework.request import Request

table_prefix = settings.TABLE_PREFIX  # 数据库表名前缀


class SoftDeleteQuerySet(models.QuerySet):
    pass


class SoftDeleteManager(models.Manager):
    """支持软删除"""

    def __init__(self, *args, **kwargs):
        self.__add_is_del_filter = False
        super(SoftDeleteManager, self).__init__(*args, **kwargs)

    def filter(self, *args, **kwargs):
        # 考虑是否主动传入is_deleted
        if not kwargs.get('is_deleted') is None:
            self.__add_is_del_filter = True
        return super(SoftDeleteManager, self).filter(*args, **kwargs)

    def get_queryset(self):
        if self.__add_is_del_filter:
            return SoftDeleteQuerySet(self.model, using=self._db).exclude(is_deleted=False)
        return SoftDeleteQuerySet(self.model).exclude(is_deleted=True)

    def get_by_natural_key(self, name):
        return SoftDeleteQuerySet(self.model).get(username=name)


class SoftDeleteModel(models.Model):
    """
    软删除模型
    一旦继承,就将开启软删除
    """
    is_deleted = models.BooleanField(verbose_name="是否软删除", help_text='是否软删除', default=False, db_index=True)
    objects = SoftDeleteManager()

    class Meta:
        abstract = True
        verbose_name = '软删除模型'
        verbose_name_plural = verbose_name

    def delete(self, using=None, soft_delete=True, *args, **kwargs):
        """
        重写删除方法,直接开启软删除
        """
        if soft_delete:
            self.is_deleted = True
            self.save(using=using)
            # 级联软删除关联对象
            for related_object in self._meta.related_objects:
                related_model = getattr(self, related_object.get_accessor_name())
                # 处理一对多和多对多的关联对象
                if related_object.one_to_many or related_object.many_to_many:
                    related_objects = related_model.all()
                elif related_object.one_to_one:
                    related_objects = [related_model]
                else:
                    continue

                for obj in related_objects:
                    obj.delete(soft_delete=True)
        else:
            super().delete(using=using, *args, **kwargs)


class CoreModel(models.Model):
    """
    核心标准抽象模型模型,可直接继承使用
    增加审计字段, 覆盖字段时, 字段名称请勿修改, 必须统一审计字段名称
    """
    id = models.BigAutoField(primary_key=True, help_text="Id", verbose_name="Id")
    description = models.CharField(max_length=255, verbose_name="描述", null=True, blank=True, help_text="描述")
    creator = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_query_name='creator_query', null=True,
                                verbose_name='创建人', help_text="创建人", on_delete=models.SET_NULL,
                                db_constraint=False)
    modifier = models.CharField(max_length=255, null=True, blank=True, help_text="修改人", verbose_name="修改人")
    dept_belong_id = models.CharField(max_length=255, help_text="数据归属部门", null=True, blank=True,
                                      verbose_name="数据归属部门")
    update_datetime = models.DateTimeField(auto_now=True, null=True, blank=True, help_text="修改时间",
                                           verbose_name="修改时间")
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="创建时间",
                                           verbose_name="创建时间")

    class Meta:
        abstract = True
        verbose_name = '核心模型'
        verbose_name_plural = verbose_name

    def get_request_user(self, request: Request):
        if getattr(request, "user", None):
            return request.user
        return None

    def get_request_user_id(self, request: Request):
        if getattr(request, "user", None):
            return getattr(request.user, "id", None)
        return None

    def get_request_user_name(self, request: Request):
        if getattr(request, "user", None):
            return getattr(request.user, "name", None)
        return None

    def get_request_user_username(self, request: Request):
        if getattr(request, "user", None):
            return getattr(request.user, "username", None)
        return None

    def common_insert_data(self, request: Request):
        data = {
            'create_datetime': datetime.now(),
            'creator': self.get_request_user(request)
        }
        return {**data, **self.common_update_data(request)}

    def common_update_data(self, request: Request):
        return {
            'update_datetime': datetime.now(),
            'modifier': self.get_request_user_username(request)
        }

    exclude_fields = [
        '_state',
        'pk',
        'id',
        'create_datetime',
        'update_datetime',
        'creator',
        'creator_id',
        'creator_pk',
        'creator_name',
        'modifier',
        'modifier_id',
        'modifier_pk',
        'modifier_name',
        'dept_belong_id',
    ]

    def get_exclude_fields(self):
        return self.exclude_fields

    def get_all_fields(self):
        return self._meta.fields

    def get_all_fields_names(self):
        return [field.name for field in self.get_all_fields()]

    def get_need_fields_names(self):
        return [field.name for field in self.get_all_fields() if field.name not in self.exclude_fields]

    def to_data(self):
        """将模型转化为字典（去除不包含字段）(注意与to_dict_data区分)。
        """
        res = {}
        for field in self.get_need_fields_names():
            field_value = getattr(self, field)
            res[field] = field_value.id if (issubclass(field_value.__class__, CoreModel)) else field_value
        return res

    @property
    def DATA(self):
        return self.to_data()

    def to_dict_data(self):
        """需要导出的字段（去除不包含字段）（注意与to_data区分）
        """
        return {field: getattr(self, field) for field in self.get_need_fields_names()}

    @property
    def DICT_DATA(self):
        return self.to_dict_data()

    def insert(self, request):
        """插入模型
        """
        assert self.pk is None, f'模型{self.__class__.__name__}还没有保存到数据中，不能手动指定ID'
        validated_data = {**self.common_insert_data(request), **self.DICT_DATA}
        return self.__class__._default_manager.create(**validated_data)

    def update(self, request, update_data: dict[str, any] = None):
        """更新模型
        """
        assert isinstance(update_data, dict), 'update_data必须为字典'
        validated_data = {**self.common_insert_data(request), **update_data}
        for key, value in validated_data.items():
            # 不允许修改id,pk,uuid字段
            if key in ['id', 'pk', 'uuid']:
                continue
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
        return self


def get_all_models_objects(model_name=None):
    """
    获取所有 models 对象
    :return: {}
    """
    settings.ALL_MODELS_OBJECTS = {}
    if not settings.ALL_MODELS_OBJECTS:
        all_models = apps.get_models()
        for item in list(all_models):
            table = {"tableName": item._meta.verbose_name, "table": item.__name__, "tableFields": []}
            for field in item._meta.fields:
                fields = {"title": field.verbose_name, "field": field.name}
                table['tableFields'].append(fields)
            settings.ALL_MODELS_OBJECTS.setdefault(item.__name__, {"table": table, "object": item})
    if model_name:
        return settings.ALL_MODELS_OBJECTS[model_name] or {}
    return settings.ALL_MODELS_OBJECTS or {}


def get_model_from_app(app_name):
    """获取模型里的字段"""
    model_module = import_module(app_name + '.models')
    exclude_models = getattr(model_module, 'exclude_models', [])
    filter_model = [
        value for key, value in model_module.__dict__.items()
        if key != 'CoreModel'
        and isinstance(value, type)
        and issubclass(value, models.Model)
        and key not in exclude_models
    ]
    model_list = []
    for model in filter_model:
        if model.__name__ == 'AbstractUser':
            continue
        fields = [{'title': field.verbose_name, 'name': field.name, 'object': field} for field in model._meta.fields]
        model_list.append({'app': app_name, 'verbose': model._meta.verbose_name, 'model': model.__name__, 'object': model, 'fields': fields})
    return model_list


def get_custom_app_models(app_name=None):
    """
    获取所有项目下的app里的models
    """
    if app_name:
        return get_model_from_app(app_name)
    all_apps = apps.get_app_configs()
    res = []
    for app in all_apps:
        if app.name.startswith('django'):
            continue
        if app.name in settings.COLUMN_EXCLUDE_APPS:
            continue
        try:
            all_models = get_model_from_app(app.name)
            if all_models:
                for model in all_models:
                    res.append(model)
        except Exception as e:
            pass
    return res
