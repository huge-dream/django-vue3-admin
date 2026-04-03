# -*- coding: utf-8 -*-
"""
RustFS (S3-compatible) 文件存储工具
"""
import uuid
from typing import Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings


def get_rustfs_client():
    """
    创建 RustFS S3 客户端
    """
    client = boto3.client(
        's3',
        endpoint_url=f"{'https' if settings.RUSTFS_SECURE else 'http'}://{settings.RUSTFS_ENDPOINT}",
        aws_access_key_id=settings.RUSTFS_ACCESS_KEY,
        aws_secret_access_key=settings.RUSTFS_SECRET_KEY,
        region_name=settings.RUSTFS_REGION or 'us-east-1',
        config=Config(signature_version='s3v4'),
    )
    return client


def rustfs_upload_file(file_obj, file_name: str) -> Optional[str]:
    """
    上传文件到 RustFS

    Args:
        file_obj: 文件对象 (InMemoryUploadedFile 或 UploadedFile)
        file_name: 原始文件名

    Returns:
        文件访问URL，失败返回 None
    """
    try:
        # 生成唯一文件名 (uuid前缀避免冲突)
        ext = file_name.split('.')[-1] if '.' in file_name else ''
        unique_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex

        # 路径前缀处理
        path_prefix = getattr(settings, 'RUSTFS_PATH_PREFIX', '')
        if path_prefix:
            path_prefix = path_prefix.strip('/') + '/'
        object_name = f"{path_prefix}{unique_name}"

        # 获取文件内容
        file_obj.seek(0)
        file_content = file_obj.read()

        # 上传
        client = get_rustfs_client()
        client.put_object(
            Bucket=settings.RUSTFS_BUCKET,
            Key=object_name,
            Body=file_content,
            ContentType=getattr(file_obj, 'content_type', 'application/octet-stream'),
        )

        # 生成访问URL
        file_url = rustfs_get_file_url(object_name)
        return file_url

    except ClientError as e:
        print(f"RustFS upload error: {e}")
        return None
    except Exception as e:
        print(f"RustFS upload unexpected error: {e}")
        return None


def rustfs_delete_file(file_url: str) -> bool:
    """
    从 RustFS 删除文件

    Args:
        file_url: 文件完整URL或 object_key

    Returns:
        删除成功返回 True，否则 False
    """
    try:
        # 从URL中提取 object_key
        object_key = file_url
        if settings.RUSTFS_ENDPOINT in file_url:
            # 提取 /bucket/key 部分
            parts = file_url.split(settings.RUSTFS_BUCKET + '/')
            if len(parts) > 1:
                object_key = parts[-1]
            else:
                return True  # URL格式不对，当作已删除

        client = get_rustfs_client()
        client.delete_object(Bucket=settings.RUSTFS_BUCKET, Key=object_key)
        return True
    except ClientError as e:
        print(f"RustFS delete error: {e}")
        return False


def rustfs_get_file_url(object_key: str) -> str:
    """
    获取文件访问URL

    Args:
        object_key: 对象存储的key

    Returns:
        完整的文件访问URL
    """
    scheme = 'https' if settings.RUSTFS_SECURE else 'http'
    endpoint = settings.RUSTFS_ENDPOINT
    bucket = settings.RUSTFS_BUCKET
    return f"{scheme}://{endpoint}/{bucket}/{object_key}"
