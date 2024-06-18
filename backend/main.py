import multiprocessing
import os
import sys
import time
import threading
import webbrowser

root_path = os.getcwd()
sys.path.append(root_path)
import uvicorn
from pathlib import Path
from application.settings import LOGGING

BASE_DIR = Path(__file__).resolve().parent.parent
url = "http://127.0.0.1:8000/web/"


def open_browser_after_delay(url, delay):
    time.sleep(delay)
    webbrowser.open(url)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    threading.Thread(target=open_browser_after_delay, args=(url, 3)).start()
    uvicorn.run("application.asgi:application", reload=False, host="0.0.0.0", port=8000, workers=4,
                log_config=LOGGING)
