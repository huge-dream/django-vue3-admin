# -*- coding: utf-8 -*-

import oss2
from rest_framework.exceptions import ValidationError

from application import dispatch


# 进度条
# 当无法确定待上传的数据长度时，total_bytes的值为None。
def percentage(consumed_bytes, total_bytes):
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        print('\r{0}% '.format(rate), end='')


def ali_oss_upload(file, file_name):
    """
    阿里云OSS上传
    """
    try:
        file.seek(0)
        file_read = file.read()
    except Exception as e:
        file_read = file
    if not file:
        raise ValidationError('请上传文件')
    # 转存到oss
    path_prefix = dispatch.get_system_config_values("file_storage.aliyun_path")
    if not path_prefix.endswith('/'):
        path_prefix = path_prefix + '/'
    if path_prefix.startswith('/'):
        path_prefix = path_prefix[1:]
    base_fil_name = f'{path_prefix}{file_name}'
    # 获取OSS配置
    # 获取的AccessKey
    access_key_id = dispatch.get_system_config_values("file_storage.aliyun_access_key")
    access_key_secret = dispatch.get_system_config_values("file_storage.aliyun_access_secret")
    auth = oss2.Auth(access_key_id, access_key_secret)
    # 这个是需要用特定的地址，不同地域的服务器地址不同，不要弄错了
    # 参考官网给的地址配置https://www.alibabacloud.com/help/zh/object-storage-service/latest/regions-and-endpoints#concept-zt4-cvy-5db
    endpoint = dispatch.get_system_config_values("file_storage.aliyun_endpoint")
    bucket_name = dispatch.get_system_config_values("file_storage.aliyun_bucket")
    if bucket_name.endswith(endpoint):
        bucket_name = bucket_name.replace(f'.{endpoint}', '')
    # 你的项目名称，类似于不同的项目上传的图片前缀url不同
    bucket = oss2.Bucket(auth, endpoint, bucket_name)  # 项目名称
    # 生成外网访问的文件路径
    aliyun_cdn_url = dispatch.get_system_config_values("file_storage.aliyun_cdn_url")
    if aliyun_cdn_url:
        if aliyun_cdn_url.endswith('/'):
            aliyun_cdn_url = aliyun_cdn_url[1:]
        file_path = f"{aliyun_cdn_url}/{base_fil_name}"
    else:
        file_path = f"https://{bucket_name}.{endpoint}/{base_fil_name}"
    # 这个是阿里提供的SDK方法
    res = bucket.put_object(base_fil_name, file_read, progress_callback=percentage)
    # 如果上传状态是200 代表成功 返回文件外网访问路径
    if res.status == 200:
        return file_path
    else:
        return None
