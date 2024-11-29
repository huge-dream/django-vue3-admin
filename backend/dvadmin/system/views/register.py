from datetime import datetime, timedelta

from captcha.views import CaptchaStore
from django.core.validators import EmailValidator
from django.db.models import Q
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from application import dispatch
from dvadmin.system.models import Users, Role, Dept
from dvadmin.utils.request_util import save_login_log
from dvadmin.utils.validator import CustomValidationError


# noinspection PyUnresolvedReferences
class RegisterSerializer(TokenObtainPairSerializer):
    captcha = serializers.CharField(
        max_length=6, required=False, allow_null=True, allow_blank=True
    )

    class Meta:
        model = Users
        fields = ["username", "password", "name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_code = None

    default_error_messages = {"no_active_account": "账号/密码错误"}

    @staticmethod
    def validate_email_format(email):
        """
        验证邮箱格式是否正确
        """
        email_validator = EmailValidator()
        try:
            email_validator(email)
        except serializers.ValidationError:
            raise CustomValidationError("邮箱格式不正确")

    # noinspection PyTypeChecker
    def validate(self, attrs):
        if not dispatch.get_system_config_values("register.register_state"):
            raise CustomValidationError("当前系统不允许注册，请联系管理员")
        captcha = self.initial_data.get("captcha", None)
        if dispatch.get_system_config_values("register.register_captcha_state"):
            if captcha is None:
                raise CustomValidationError("验证码不能为空")
            self.image_code = CaptchaStore.objects.filter(
                id=self.initial_data["captchaKey"]
            ).first()
            five_minute_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if self.image_code and five_minute_ago > self.image_code.expiration:
                self.image_code and self.image_code.delete()
                raise CustomValidationError("验证码过期")
            else:
                if self.image_code and (
                        self.image_code.response == captcha
                        or self.image_code.challenge == captcha
                ):
                    self.image_code and self.image_code.delete()
                else:
                    self.image_code and self.image_code.delete()
                    raise CustomValidationError("图片验证码错误")
        username = attrs["username"]
        if not username.isalnum():
            raise CustomValidationError("用户名只能包含字母和数字")

        email = self.initial_data["email"]
        self.validate_email_format(email)

        try:
            user = Users.objects.get(
                Q(username=attrs['username']) | Q(email=attrs['username']) | Q(mobile=attrs['username']))
            if user:
                raise CustomValidationError("该账号已被注册")
        except Users.DoesNotExist:
            pass

        try:
            user = Users.objects.create_user(
                username=attrs["username"],
                password=attrs["password"],
                name=self.initial_data["name"],
                email=email,
                pwd_change_count=1,
            )
            if dispatch.get_system_config_values("register.default_dept"):
                user.dept.add(Dept.objects.get(name=dispatch.get_system_config_values("register.default_dept")))
            else:
                user.dept.add(Dept.objects.first())
            if dispatch.get_system_config_values("register.default_role"):
                user.role.add(Role.objects.get(name=dispatch.get_system_config_values("register.default_role")))
            else:
                user.role.add(Role.objects.first())
            user.save()
            data = super().validate(attrs)
            data["name"] = user.name
            data["userId"] = user.id
            data["avatar"] = user.avatar
            data['user_type'] = user.user_type
            dept = getattr(user, 'dept', None)
            if dept:
                data['dept_info'] = {
                    'dept_id': dept.id,
                    'dept_name': dept.name,
                }
            role = getattr(user, 'role', None)
            if role:
                data['role_info'] = role.values('id', 'name', 'key')
            request = self.context.get("request")
            request.user = user
            # 记录登录日志
            save_login_log(request=request)
            return {"code": 2000, "msg": "请求成功", "data": data}
        except Exception as e:
            raise CustomValidationError(f"注册失败,{e}")


class RegisterView(TokenObtainPairView):
    """
    注册接口
    """
    serializer_class = RegisterSerializer
    permission_classes = []
