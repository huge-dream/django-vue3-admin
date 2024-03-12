from functools import wraps

from django.db.models import Func, F, OuterRef, Exists
from django.test import TestCase
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "application.settings")
django.setup()
from dvadmin.system.models import Menu, RoleMenuPermission, RoleMenuButtonPermission, MenuButton


import time

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        run_time = end_time - start_time
        print(f"{func.__name__} ran in {run_time:.6f} seconds")
        return result
    return wrapper

@timing_decorator
def getMenu():
    data = []
    queryset = Menu.objects.filter(status=1, is_catalog=False).values('name', 'id')
    for item in queryset:
        parent_list = Menu.get_all_parent(item['id'])
        names = [d["name"] for d in parent_list]
        completeName = "/".join(names)
        isCheck = RoleMenuPermission.objects.filter(
            menu__id=item['id'],
            role__id=1,
        ).exists()
        mbCheck = RoleMenuButtonPermission.objects.filter(
        menu_button = OuterRef("pk"),
        role__id=1,
        )
        btns = MenuButton.objects.filter(
            menu__id=item['id'],
        ).annotate(isCheck=Exists(mbCheck)).values('id', 'name', 'value', 'isCheck',data_range=F('menu_button_permission__data_range'))
        # print(b)
        dicts = {
            'name': completeName,
            'id': item['id'],
            'isCheck': isCheck,
            'btns':btns
        }
        print(dicts)
        data.append(dicts)
    # print(data)

if __name__ == '__main__':
    getMenu()