from django.db import models
from django.utils import timezone

from dvadmin.system.models import Users
from dvadmin.utils.models import CoreModel, table_prefix


# Create your models here.

# {
#   "access_token": "ACCESSTOKENEXAMPLE",
#   "token_type": "Bearer",
#   "refresh_token": "REFRESHTOKENEXAMPLE",
#   "expires_in": 259200,
#   "scope": "scope.file.editable,scope.folder.creatable",
#   "user_id": "bcb50c8a4b724d86bbcf6fc64c5e2b22"
# }

class TencentDocxUser(CoreModel):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, verbose_name='用户')
    access_token = models.CharField(max_length=512, verbose_name='访问令牌')
    access_expires_in = models.DateTimeField(verbose_name='访问过期时间')
    refresh_token = models.CharField(max_length=512, verbose_name='刷新令牌')
    refresh_expires_in = models.DateTimeField(verbose_name='刷新过期时间')
    scope = models.CharField(max_length=512, verbose_name='范围')
    tencent_user_id = models.CharField(max_length=64, verbose_name='用户ID')

    class Meta:
        db_table = table_prefix + 'tencent_docx_user'
        verbose_name = '腾讯文档用户'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def save(self, *args, **kwargs):
        if self.access_expires_in and timezone.is_naive(self.access_expires_in):
            self.access_expires_in = timezone.make_aware(self.access_expires_in)
        if self.refresh_expires_in and timezone.is_naive(self.refresh_expires_in):
            self.refresh_expires_in = timezone.make_aware(self.refresh_expires_in)

# class TencentDocxDDDD(CoreModel):
#     ...
