# -*- coding: utf-8 -*-


from django.db.models import F
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dvadmin.system.models import RoleMenuPermission, Menu, MenuButton
from dvadmin.utils.json_response import DetailResponse, ErrorResponse
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.viewset import CustomModelViewSet


class RoleMenuPermissionSerializer(CustomModelSerializer):
    """
    菜单按钮-序列化器
    """

    class Meta:
        model = RoleMenuPermission
        fields = "__all__"
        read_only_fields = ["id"]


class RoleMenuPermissionInitSerializer(CustomModelSerializer):
    """
    初始化菜单按钮-序列化器
    """

    class Meta:
        model = RoleMenuPermission
        fields = "__all__"
        read_only_fields = ["id"]

class RoleMenuPermissionCreateUpdateSerializer(CustomModelSerializer):
    """
    初始化菜单按钮-序列化器
    """

    class Meta:
        model = RoleMenuPermission
        fields = "__all__"
        read_only_fields = ["id"]


class RoleMenuPermissionViewSet(CustomModelViewSet):
    """
    菜单按钮接口
    list:查询
    create:新增
    update:修改
    retrieve:单例
    destroy:删除
    """
    queryset = RoleMenuPermission.objects.all()
    serializer_class = RoleMenuPermissionSerializer
    create_serializer_class = RoleMenuPermissionCreateUpdateSerializer
    update_serializer_class = RoleMenuPermissionCreateUpdateSerializer
    extra_filter_class = []

    @action(methods=['get'],detail=False)
    def menu_permission_tree(self,request):
        """
        获取菜单按钮树
        """
        # params = request.query_params
        # role_id = params.get('role',None)
        # if role_id is None:
        #     return ErrorResponse(msg="未获取到角色")
        if request.user.is_superuser:
            queryset = Menu.objects.filter(status=1).values("id", "name", "parent_id")
        else:
            role_id = request.user.role.values_list('id', flat=True)
            menu_list = RoleMenuPermission.objects.filter(role__in=role_id).values_list('menu_id', flat=True)
            queryset = Menu.objects.filter(status=1, id__in=menu_list).values('id','name', "parent_id").all()
        return DetailResponse(data=queryset)

    @action(methods=['get'],detail=False)
    def get_menu_permission_checked(self,request):
        """
        获取已授权的菜单
        """
        params = request.query_params
        role_id = params.get('role',None)
        if role_id is None:
            return ErrorResponse(msg="未获取到角色")
        menu_list = RoleMenuPermission.objects.filter(role__in=role_id).values_list('menu_id', flat=True)
        queryset = Menu.objects.filter(status=1, id__in=menu_list).values_list('id',flat=True)
        return DetailResponse(data=queryset)

    @action(methods=['post'],detail=False)
    def save_menu_permission(self,request):
        """
        保存页面菜单授权
        :param request:
        :return:
        """
        body = request.data
        role_id = body.get('role',None)
        if role_id is None:
            return ErrorResponse(msg="未获取到角色参数")
        menu_list = body.get('menu',None)
        if menu_list is None:
            return ErrorResponse(msg="未获取到菜单参数")
        obj_list = RoleMenuPermission.objects.filter(role__id=role_id).values_list('menu__id',flat=True)
        old_set = set(obj_list)
        new_set = set(menu_list)
        #need_update = old_set.intersection(new_set) # 需要更新的
        need_del = old_set.difference(new_set) # 需要删除的
        need_add = new_set.difference(old_set) # 需要新增的
        RoleMenuPermission.objects.filter(role__id=role_id,menu__in=list(need_del)).delete()
        data = [{"role": role_id, "menu": item} for item in list(need_add)]
        serializer = RoleMenuPermissionSerializer(data=data,many=True,request=request)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return DetailResponse(msg="保存成功",data=serializer.data)
