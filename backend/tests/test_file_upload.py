"""
RustFS 文件上传集成测试

依赖: 真实的 RustFS 服务运行在 RUSTFS_ENDPOINT (192.168.80.90:9000)
测试前确保:
  1. RustFS 服务已启动
  2. bucket "pis-media" 已创建
  3. RUSTFS_ACCESS_KEY / RUSTFS_SECRET_KEY 正确配置
"""
import io
import pytest
from django.conf import settings
from rest_framework import status


CODE_SUCCESS = 2000
CODE_ERROR = 4000


@pytest.mark.django_db
class TestFileUpload:
    """文件上传 API 测试"""

    def test_upload_file_success(self, authenticate):
        """POST 上传文件返回成功 + RustFS URL"""
        file_content = b"Hello, RustFS!"
        file_obj = io.BytesIO(file_content)
        file_obj.name = "test.txt"

        response = authenticate.post(
            "/api/system/file/",
            data={"file": file_obj},
            format="multipart",
        )

        assert response.data["code"] == CODE_SUCCESS, f"上传失败: {response.data}"
        assert "file_url" in response.data["data"]
        file_url = response.data["data"]["file_url"]
        # 验证 URL 指向 RustFS
        assert settings.RUSTFS_ENDPOINT in file_url, f"文件 URL 非 RustFS 地址: {file_url}"
        assert file_url.startswith("http://") or file_url.startswith("https://")

    def test_upload_file_unauthenticated(self, api_client):
        """未认证请求上传文件返回错误码"""
        file_content = b"Unauthorized file"
        file_obj = io.BytesIO(file_content)
        file_obj.name = "unauth.txt"

        response = api_client.post(
            "/api/system/file/",
            data={"file": file_obj},
            format="multipart",
        )
        # 无认证时返回 4000 或非 2000
        assert response.data["code"] == CODE_ERROR

    def test_upload_image_success(self, authenticate):
        """POST 上传图片返回成功 + image file_type"""
        # GIF 格式最小文件 (1x1 透明像素)
        gif_bytes = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00"
            b"\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00"
            b"\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44"
            b"\x01\x00\x3b"
        )
        file_obj = io.BytesIO(gif_bytes)
        file_obj.name = "test.gif"

        response = authenticate.post(
            "/api/system/file/",
            data={"file": file_obj},
            format="multipart",
        )

        assert response.data["code"] == CODE_SUCCESS, f"图片上传失败: {response.data}"
        file_url = response.data["data"]["file_url"]
        assert settings.RUSTFS_ENDPOINT in file_url

    def test_upload_without_file(self, authenticate):
        """POST 不带文件返回错误码"""
        response = authenticate.post("/api/system/file/", data={}, format="multipart")
        # 不带文件应该失败
        assert response.data["code"] == CODE_ERROR
