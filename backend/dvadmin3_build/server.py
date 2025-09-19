import json
import os
import re
import signal
import subprocess
import webbrowser
import time
import threading
from pathlib import Path

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, QTimer, pyqtSignal, Qt
from PyQt6.QtNetwork import QLocalServer
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QTextCharFormat, QColor, QTextCursor
from PyQt6 import QtCore, QtGui, QtWidgets

import sys


# # 编译ui
# pyuic6 dvadmin_main.ui -o dvadmin_main.py
# 由于编译问题，把dvadmin_main.py代码复制到本脚本中
class Ui_DvadminManager(object):
    def setupUi(self, DvadminManager):
        DvadminManager.setObjectName("DvadminManager")
        DvadminManager.resize(400, 300)
        DvadminManager.setMinimumSize(QtCore.QSize(400, 300))
        DvadminManager.setMaximumSize(QtCore.QSize(400, 300))
        self.label = QtWidgets.QLabel(parent=DvadminManager)
        self.label.setGeometry(QtCore.QRect(10, 13, 60, 21))
        self.label.setObjectName("label")
        self.status_label = QtWidgets.QLabel(parent=DvadminManager)
        self.status_label.setGeometry(QtCore.QRect(80, 12, 60, 21))
        self.status_label.setObjectName("status_label")
        self.start_button = QtWidgets.QPushButton(parent=DvadminManager)
        self.start_button.setGeometry(QtCore.QRect(210, 10, 81, 26))
        self.start_button.setObjectName("start_button")
        self.stop_button = QtWidgets.QPushButton(parent=DvadminManager)
        self.stop_button.setGeometry(QtCore.QRect(310, 9, 81, 26))
        self.stop_button.setObjectName("stop_button")
        self.line = QtWidgets.QFrame(parent=DvadminManager)
        self.line.setGeometry(QtCore.QRect(0, 40, 401, 16))
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.log_label = QtWidgets.QTextEdit(parent=DvadminManager)
        self.log_label.setGeometry(QtCore.QRect(-1, 47, 411, 261))
        self.log_label.setObjectName("log_label")

        self.retranslateUi(DvadminManager)
        QtCore.QMetaObject.connectSlotsByName(DvadminManager)

    def retranslateUi(self, DvadminManager):
        _translate = QtCore.QCoreApplication.translate
        DvadminManager.setWindowTitle(_translate("DvadminManager", "服务管理器"))
        self.label.setText(_translate("DvadminManager", "运行状态："))
        self.status_label.setText(_translate("DvadminManager", "未启动"))
        self.start_button.setText(_translate("DvadminManager", "启动服务"))
        self.stop_button.setText(_translate("DvadminManager", "结束服务"))
        self.log_label.setHtml(_translate("DvadminManager", ""))


class SelectWorkerSignals(QObject):
    result = pyqtSignal(str)
    stop = pyqtSignal(bool)


list_process = []


class ServerWorkerSignals(QObject):
    result = pyqtSignal(str)


class SelectWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = SelectWorkerSignals()
        self.is_run = True

    def run(self):
        # 模拟异步操作
        import time
        import psutil
        while self.is_run:
            # 遍历进程列表,结束即关闭服务
            # 获取所有正在运行的进程列表
            processes = psutil.process_iter()
            new_list_process = []
            for process in processes:
                # 如果进程名称包含"uvicorn"，则进行监控
                if process.pid in list_process:
                    new_list_process.append(process.pid)
            if list_process and not new_list_process:
                self.signals.result.emit("异步,进程不存在！")
            # 等待1秒
            time.sleep(1)

    def handle_stop_result(self, result):
        """
        异步获取进程结果后执行
        """
        self.is_run = result


class ServerWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = ServerWorkerSignals()

    def run(self):
        # 启动dvadmin服务
        import os
        print("启动dvadmin服务")
        # import main
        # main.run()
        # 定义要执行的命令
        command = f"./main"
        if os.sys.platform.startswith('win'):
            # Windows操作系统
            print("当前环境是Windows", Path(__file__).resolve().parent)
            print("当前环境是Windows", Path(__file__).resolve())
            command = f"{Path(__file__).resolve().parent.parent}/main.exe"
        elif os.sys.platform.startswith('linux'):
            # Linux操作系统
            print("当前环境是Linux")
        elif os.sys.platform.startswith('darwin'):
            # macOS操作系统
            print("当前环境是macOS")
            command = f"{Path(__file__).resolve().parent.parent}/MacOS/main"
        else:
            # 其他操作系统
            print("当前环境是其他操作系统")
        self.signals.result.emit(json.dumps({"code": 2001, "msg": command}))
        global list_process
        # 使用subprocess.Popen执行命令
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.signals.result.emit(json.dumps({"code": 2000, "msg": "服务启动成功..."}))
        # 持续获取输出结果
        pid = process.pid
        list_process.append(pid)
        for line in process.stdout:
            match = re.search(r'Started server process \[(\d+)\]', line)
            # 判断是否匹配成功
            if match:
                # 获取匹配到的数字
                number = match.group(1)
                list_process.append(number)
                list_process = list(set(list_process))
            self.signals.result.emit(json.dumps({"code": 2001, "msg": line.replace('\n', '')}))
        # 等待进程结束
        process.wait()


class MainWindow(QMainWindow, Ui_DvadminManager):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 开始、结束按钮
        self.start_button.clicked.connect(self.start_service)
        self.stop_button.clicked.connect(self.stop_service)
        # 托盘按钮及事件
        self.tray_icon = QSystemTrayIcon(QIcon(os.path.join(Path(__file__).resolve().parent, 'static','logo.icns')), self)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_menu = QMenu(self)
        self.tray_menu.addAction(self.start_button.text(), self.start_service)
        self.tray_menu.addAction(self.stop_button.text(), self.stop_service)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction("退出", QApplication.quit)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

        self.log_label.setReadOnly(True)

        # 信号
        self.select_worker = SelectWorker()
        self.select_worker.signals.result.connect(self.handle_select_result)
        self.select_worker.signals.stop.connect(self.select_worker.handle_stop_result)
        self.server_worker = ServerWorker()
        self.server_worker.signals.result.connect(self.handle_server_servers)
        # 异步
        self.select_threadpool = QThreadPool()
        self.server_threadpool = QThreadPool()

    def handle_select_result(self, result):
        """
        异步获取进程结果后执行
        """
        self.append_to_log('服务进程异常，服务已停止...', color='red')
        global list_process
        list_process = []
        self.status_label.setText("已停止")
        self.status_label.setStyleSheet("color: red;")

    def handle_server_servers(self, result):
        """
        启动服务
        """
        json_result = json.loads(result)
        if json_result.get('code') == 2000:
            self.append_to_log(json_result.get('msg'), color='green')
            # 启动成功打开浏览器
            url = "http://127.0.0.1:8000/web/"
            def open_browser_after_delay(url, delay):
                time.sleep(delay)
                webbrowser.open(url)

            threading.Thread(target=open_browser_after_delay, args=(url, 3)).start()
            self.status_label.setText("运行中")
            self.status_label.setStyleSheet("color: green;")
        elif json_result.get('code') == 2001:
            self.append_to_log(json_result.get('msg'))
        else:
            self.append_to_log(json_result.get('msg'), color='red')
            self.status_label.setText("已停止")
            self.status_label.setStyleSheet("color: red;")

    def append_to_log(self, message, color=None):
        """
        添加日志颜色
        """
        cursor = self.log_label.textCursor()
        format = QTextCharFormat()
        if color:
            if color == "green":
                format.setForeground(QColor("green"))
            elif color == "red":
                format.setForeground(QColor("red"))
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(message, format)
        cursor.insertBlock()
        self.log_label.setTextCursor(cursor)
        self.log_label.ensureCursorVisible()
        self.log_label.verticalScrollBar().setValue(self.log_label.verticalScrollBar().maximum())

    def start_service(self):
        global list_process
        if not list_process:
            # 启动服务,执行启动脚本
            self.server_threadpool.clear()
            self.select_threadpool.clear()
            self.select_worker.signals.stop.emit(True)
            self.select_threadpool.startOnReservedThread(self.select_worker.run)
            self.server_threadpool.startOnReservedThread(self.server_worker.run)
            self.status_label.setText("正在启动中")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.append_to_log("服务已启动...")

    def stop_service(self):
        """
        停止服务
        """
        global list_process
        if list_process:
            for pid in list_process:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                except Exception as e:
                    print('Exception', e)
                    pass
            list_process = []
        self.select_worker.signals.stop.emit(False)
        self.select_threadpool.clear()
        self.server_threadpool.clear()
        self.status_label.setText("已停止")
        self.status_label.setStyleSheet("color: red;")
        self.service_running = False
        self.append_to_log("服务已停止...", color='red')

    def tray_icon_activated(self, reason):
        """
        托盘激活
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.showNormal()
            self.activateWindow()

    def showEvent(self, event):
        # 自定义的显示事件处理
        if self.status_label.text() != '已停止':
            self.select_worker.signals.stop.emit(True)
            self.select_threadpool.startOnReservedThread(self.select_worker.run)
        return super().showEvent(event)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.select_worker.signals.stop.emit(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    server = QLocalServer()
    if server.listen('DVAServer'):
        app.setQuitOnLastWindowClosed(False)
        app.setWindowIcon(QIcon(os.path.join(Path(__file__).resolve().parent, 'static','logo.icns')))
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        message_box = QMessageBox(QMessageBox.Icon.Information, 'Information', '应用程序已在运行')
        message_box.exec()
        sys.exit(0)  # 如果已有实例在运行，则退出应用程序
