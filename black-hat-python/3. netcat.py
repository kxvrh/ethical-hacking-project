import argparse
from audioop import add
import socket
import shlex
import subprocess       # 进程创捷接口
import sys
import textwrap
import threading

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    # 在本机运行一条命令,并返回该命令的输出
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)

    return output.decode()

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 格外扩展, SOL_SOCKET基本套接口, SO_REUSEADDR允许重用本地地址和端口
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            # 连接到target后, 若此时缓冲区有数据, 先将数据发送
            self.socket.send(self.buffer)

        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        print(f'[*] Start listening on {self.args.target}:{self.args.port}')
        while True:
            client_socket, address = self.socket.accept()
            print(f'[*] Received connection from {address[0]}:{address[1]}')
            # 创建进程指向handle函数, 传递已连接的socket参数
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    def handle(self, client_socket):
   
        if self.args.execute:
            # 执行命令
            output = execute(self.args.execute)
            # 将执行结果发送出去
            client_socket.send(output.encode())

        elif self.args.upload:
            # 上传文件
            file_buffer = b''
            while True:
                # 接收文件内容
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload, 'wb')as f:
                # 写入指定文件
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())
        
        elif self.args.command:
            # 创建shell
            cmd_buffer = b''
            while True:
                try:
                    # 等待发送方的指令
                    client_socket.send(b'BHP #> ')
                    while '\n' not in cmd_buffer.decode():
                        # 接受指令
                        cmd_buffer += client_socket.recv(64)
                    # 执行指令
                    response = execute(cmd_buffer.decode())
                    if response:
                        # 将执行结果发送出去
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()





if __name__ == "__main__":
    # 创建一个带命令行界面的程序
    parser = argparse.ArgumentParser(
        description='BHP Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example:
        netcat.py -t 192.168.1.108 -p 5555 -l -c                        # command shell
        netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt             # upload to file
        netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\"    # command shell
        echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135                # echo text to server port 135
        netcat.py -t 192.168.1.108 -p 5555                              # connect to the server
        '''))

    # 添加6个参数
    parser.add_argument('-c', '--command', action='store_true', help='command shell')       # 打开交互式的命令行shell
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    
    args = parser.parse_args()

    if args.listen:     # 若确定了程序要监听(即为接收方, 收到-c, -e, -u, 需要使用-l)
        buffer = ''     # 缓冲区填上空白数据
    
    else:               # 发送数据(即为发送方, -t, -p指定接收方)
        # 一直从stdin读数据, 直到文件结束符(EOF) --> ctrl + D
        buffer = sys.stdin.read()

    nc = NetCat(args, buffer.encode())
    nc.run()