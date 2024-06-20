import multiprocessing
import os
import sys

root_path = os.getcwd()
sys.path.append(root_path)
import uvicorn
from application.settings import LOGGING

if __name__ == '__main__':
    multiprocessing.freeze_support()
    uvicorn.run("application.asgi:application", reload=False, host="0.0.0.0", port=8000, workers=4,
                log_config=LOGGING)
