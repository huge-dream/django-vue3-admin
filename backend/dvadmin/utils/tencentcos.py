# -*- coding: utf-8 -*-
from rest_framework.exceptions import ValidationError

from application import dispatch
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


# 进度条
# 当无法确定待上传的数据长度时，total_bytes的值为None。
def percentage(consumed_bytes, total_bytes):
    if total_bytes:
        rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
        print('\r{0}% '.format(rate), end='')

def tencent_cos_upload(file, file_name):
    try:
        file.seek(0)
        file_read = file.read()
    except Exception as e:
        file_read = file
    if not file:
        raise ValidationError('请上传文件')
    # 生成文件名
    path_prefix = dispatch.get_system_config_values("file_storage.tencent_path")
    if not path_prefix.endswith('/'):
        path_prefix = path_prefix + '/'
    if path_prefix.startswith('/'):
        path_prefix = path_prefix[1:]
    base_fil_name = f'{path_prefix}{file_name}'
    # 获取cos配置
    # 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
    secret_id = dispatch.get_system_config_values("file_storage.tencent_secret_id") # 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
    secret_key = dispatch.get_system_config_values("file_storage.tencent_secret_key")  # 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
    region = dispatch.get_system_config_values("file_storage.tencent_region") # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket                          # COS 支持的所有 region 列表参见https://cloud.tencent.com/document/product/436/6224
    bucket = dispatch.get_system_config_values("file_storage.tencent_bucket")  # 要访问的桶名称
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)
    # 访问地址
    base_file_url = f'https://{bucket}.cos.{region}.myqcloud.com'
    # 生成外网访问的文件路径
    if base_file_url.endswith('/'):
        file_path = base_file_url + base_fil_name
    else:
        file_path = f'{base_file_url}/{base_fil_name}'
    # 这个是阿里提供的SDK方法 bucket是调用的4.1中配置的变量名
    try:
        response = client.put_object(
            Bucket=bucket,
            Body=file_read,
            Key=base_fil_name,
            EnableMD5=False
        )
        return file_path
    except:
        return None
