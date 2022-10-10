import contextlib
import os
import queue
import requests
import sys
import threading
import time

# 不想扫描的文件扩展名
FILTER = ['.jpg', '.gif', 'png', '.css']
TARGET = 'http://boodelyboo.com/wordpress'
THREAD = 10

# 存储最后实际扫描到的路径
answers = queue.Queue()
# 存储准备扫描的路径
web_paths = queue.Queue()

def gather_paths():
    # 遍历本地web应用安装目录里的所有文件和目录
    for root, _, files in os.walk('.'):
        for fname in files:
            if os.path.splitext(fname)[1] in FILTER:
                continue
            path = os.path.join(root, fname)
            if path.startswith('.'):
                path = path[1:]
            print(path)
            web_paths.put(path)

# 创建简单的上下文管理器
@contextlib.contextmanager
def chdir(path):
    this_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    # 不论try中出现什么异常, finally代码块最后一定会执行
    finally:
        os.chdir(this_dir)

if __name__ == '__main__':
    with chdir('/root/Downloads/wordpress'):
        gather_paths()
    input('Press return to continue.')