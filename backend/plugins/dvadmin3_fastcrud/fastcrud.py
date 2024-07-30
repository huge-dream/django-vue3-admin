# -*- coding: utf-8 -*-
# 如果你的项目和设置文件位于同一目录下，假设settings.py的路径如下：
import os
import django



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
# 加载Django环境
django.setup()
from datetime import datetime
from django.db import models
from jinja2 import Environment, FileSystemLoader
from visualization.models import Camera, SupplyOrderDetail
from application.settings import BASE_DIR
def model_to_dict(model_class):
    field_descriptions = {}

    for field in model_class._meta.fields:
        field_type = {
            models.CharField: 'text',
            models.TextField: 'textarea',
            models.IntegerField: 'number',
            models.FloatField: 'number',
            models.DateTimeField: 'datetime',
            models.BooleanField: 'boolean',
            # 添加更多字段类型映射...
        }.get(type(field), 'unknown')

        # 字段描述
        field_config = {
            'title': field.verbose_name.title(),
            'type': field_type,
        }

        if field.choices:
            field_config['type'] = 'select'
            field_config['enum'] = [{"label":choice[1],"value":choice[0]} for choice in field.choices]
            field_config['label'] = "label"
            field_config['value'] = "value"

        field_descriptions[field.name] = field_config

    return field_descriptions


def CreateCrud(model_class,directory_path):
    """
    @param model_class: Django模型类
    @param directory_path: 生成的文件目录
    @return:
    """
    model_fields = model_to_dict(model_class)
    print(model_fields)
    # Jinja2模板加载器
    env = Environment(loader=FileSystemLoader(''))
    template = env.get_template('./temp/crud_tsx.j2')
    # 渲染模板
    output = template.render(
        model_name=f"{model_class.__name__}",
        fields=model_fields,
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    # 写入到.ts文件
    with open(f"{directory_path}/crud.tsx", "w",encoding="utf-8") as crud_file:
        crud_file.write(output)
        print("创建crud.ts文件成功")

def CreateIndex(model_class,directory_path):
    """
    @param model_class: Django模型类
    @param directory_path: 生成的文件目录
    @return:
    """
    # Jinja2模板加载器
    env = Environment(loader=FileSystemLoader(''))
    template = env.get_template('./temp/index_vue.j2')
    # 渲染模板
    output = template.render(
        model_name=f"{model_class.__name__}",
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    # 写入到.ts文件
    with open(f"{directory_path}/index.vue", "w", encoding="utf-8") as index_file:
        index_file.write(output)
        print("创建index.vue文件成功")

def CreateApi(model_class,directory_path):
    """
    @param model_class: Django模型类
    @param directory_path: 生成的文件目录
    @return:
    """
    # Jinja2模板加载器
    env = Environment(loader=FileSystemLoader(''))
    template = env.get_template('./temp/api_ts.j2')
    # 渲染模板
    output = template.render(
        model_name=f"{model_class.__name__}",
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    # 写入到.ts文件
    with open(f"{directory_path}/api.ts", "w", encoding="utf-8") as api_file:
        api_file.write(output)
        print("创建api.ts文件成功")

def FastCrud():
    model_class = SupplyOrderDetail
    # 创建目录（如果不存在）
    # 获取项目根目录
    print(BASE_DIR)
    # 拼接目录路径
    directory_path = os.path.join(BASE_DIR, f'crudFiles/{model_class.__name__}')
    print(directory_path)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    CreateCrud(model_class,directory_path)
    CreateIndex(model_class,directory_path)
    CreateApi(model_class,directory_path)

if __name__ == '__main__':
    FastCrud()