# -*- coding: utf-8 -*-
import os
from datetime import datetime

from django.apps import apps
from django.core.management import BaseCommand
from django.db import models
from jinja2 import Environment, FileSystemLoader

from application.settings import BASE_DIR


def is_valid_model(model_class):
    # 使用这个函数来获取所有模型
    model_instance = None
    for model in apps.get_models():
        if model.__name__ == model_class:
            model_instance = model
    return model_instance


# noinspection PyProtectedMember
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
            field_config['enum'] = [{"label": choice[1], "value": choice[0]} for choice in field.choices]
            field_config['label'] = "label"
            field_config['value'] = "value"

        field_descriptions[field.name] = field_config

    return field_descriptions


def CreateCrud(model_class, directory_path):
    """
    @param model_class: Django模型类
    @param directory_path: 生成的文件目录
    @return:
    """
    model_fields = model_to_dict(model_class)
    # Jinja2模板加载器
    templates = os.path.abspath(os.path.join(BASE_DIR, 'plugins/dvadmin3_fastcrud/templates'))
    env = Environment(loader=FileSystemLoader(templates))

    print(env.loader.searchpath)
    # 获取当前文件目录

    template = env.get_template('crud_tsx.j2')
    # 渲染模板
    output = template.render(
        model_name=f"{model_class.__name__}",
        fields=model_fields,
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    # 写入到.ts文件
    with open(f"{directory_path}/crud.tsx", "w", encoding="utf-8") as crud_file:
        crud_file.write(output)
        print("创建crud.ts文件成功")


def CreateIndex(model_class, directory_path):
    """
    @param model_class: Django模型类
    @param directory_path: 生成的文件目录
    @return:
    """
    # Jinja2模板加载器
    templates = os.path.abspath(os.path.join(BASE_DIR, 'plugins/dvadmin3_fastcrud/templates'))
    env = Environment(loader=FileSystemLoader(templates))
    template = env.get_template('index_vue.j2')
    # 渲染模板
    output = template.render(
        model_name=f"{model_class.__name__}",
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    # 写入到.ts文件
    with open(f"{directory_path}/index.vue", "w", encoding="utf-8") as index_file:
        index_file.write(output)
        print("创建index.vue文件成功")


def CreateApi(model_class, directory_path):
    """
    @param model_class: Django模型类
    @param directory_path: 生成的文件目录
    @return:
    """
    # Jinja2模板加载器

    templates = os.path.abspath(os.path.join(BASE_DIR, 'plugins/dvadmin3_fastcrud/templates/'))
    env = Environment(loader=FileSystemLoader(templates))

    template = env.get_template('api_ts.j2')
    # 渲染模板
    output = template.render(
        model_name=f"{model_class.__name__}",
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    # 写入到.ts文件
    with open(f"{directory_path}/api.ts", "w", encoding="utf-8") as api_file:
        api_file.write(output)
        print("创建api.ts文件成功")


class Command(BaseCommand):
    help = "My custom command's description"

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            dest='model_class_name',
            help='输入model名称,快速生成crud',
        )

    def handle(self, *args, **options):
        model_class_name = options.get('model_class_name', None)
        model_class = is_valid_model(model_class_name)
        if model_class_name and model_class is not None:
            self.stdout.write(f"即将为您生成: {model_class_name} 的CRUD代码")
            # 创建目录（如果不存在）
            directory_path = os.path.join(BASE_DIR, f'crudFiles/{model_class.__name__}')
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
            CreateCrud(model_class, directory_path)
            CreateIndex(model_class, directory_path)
            CreateApi(model_class, directory_path)
            self.stdout.write(self.style.SUCCESS("生成CRUD文件成功,请看crudFiles文件夹!"))
        else:
            self.stdout.write("请输入正确的model名称")
