import json
import os
from pathlib import Path

from django.core.management.base import BaseCommand

from application.settings import BASE_DIR

from application import settings


class Command(BaseCommand):
    """
    生产初始化菜单: python manage.py build
    """

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print(args, options)
        base_path = Path(__file__).resolve().parent.parent
        # main.spec 路径
        main_spec_path = os.path.join(base_path.parent, 'main.spec')

        # 执行编译
        import subprocess
        # 执行命令
        HIDDEN_IMPORTS = ','.join(getattr(settings, 'HIDDEN_IMPORTS', []))
        command = f'export BASE_DIR="{BASE_DIR}" && export HIDDEN_IMPORTS="{HIDDEN_IMPORTS}" && rm -rf {os.path.join(BASE_DIR, "dist")} && pyinstaller -y --clean {main_spec_path}'
        if os.sys.platform.startswith('win'):
            # Windows操作系统
            # command = f'setx BASE_DIR "{BASE_DIR}" && set HIDDEN_IMPORTS "{HIDDEN_IMPORTS}" && del {os.path.join(BASE_DIR, "dist")} && pyinstaller -y --clean {main_spec_path}'
            command = f'setx BASE_DIR "{BASE_DIR}" && setx HIDDEN_IMPORTS "{HIDDEN_IMPORTS}" && pyinstaller -y --clean {main_spec_path}'
            print(command)
            print("当前环境是 Windows")
        elif os.sys.platform.startswith('linux'):
            # Linux操作系统
            print("当前环境是 Linux")
            command += f' && rm -rf {os.path.join(BASE_DIR, "build")}'
        elif os.sys.platform.startswith('darwin'):
            # macOS操作系统
            print("当前环境是 macOS")
            build_dmg_path = os.path.join(base_path.parent, 'builddmg.sh')
            # 判断logo 是否存在
            logo_path = os.path.join(BASE_DIR, 'static', 'logo.icns')
            if not os.path.exists(logo_path):
                # 文件不存在的处理逻辑
                logo_path = os.path.join(base_path.parent, 'static', 'logo.icns')
            command += f' && chmod +x {build_dmg_path} && {build_dmg_path} {os.path.join(BASE_DIR, "dist")} {logo_path}'
            command += f' && rm -rf {os.path.join(BASE_DIR, "build")}'
        print(command)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line.replace('\n', ''))
        # # 等待进程结束
        process.wait()
