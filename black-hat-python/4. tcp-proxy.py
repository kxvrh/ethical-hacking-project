import re
from string import printable
import sys
import socket
import threading
from urllib import response

# 前256个整数对应的字符串, 在所有可打印字符的位置上, 保持原有字符不变; 不可打印的字符, 打印句点'.'
# 可打印字符的字符表示长为3个字符
HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])
# ................................ !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[.]^_`abcdefghijklmnopqrstuvwxyz{|}~
# ..................................¡¢£¤¥¦§¨©ª«¬.®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ

def hexdump(src, length=16, show=True):
    # 接收bytes或string类型的输入, 并将其转换为16进制输出
    # 可以同时以16进制或ASCII可打印字符的格式, 输出数据包的详细内容
    if isinstance(src, bytes):
        # 转换为string类型
        src = src.decode()
    
    results = list()

    for i in range(0, len(src), length):
        word = str(src[i: i+length])
        # 将整段数据转换为可打印字符的格式
        printable = word.translate(HEX_FILTER)
        # 将整段数据转换为十六进制数据
        hexa = ''.join([f'{ord(c):02X}' for c in word])
        hexwidth = length * 3
        # 将word变量起始点的偏移, 十六进制表示, 可打印字符表示打包成一行字符串
        results.append(f'{i:04X} {hexa:<{hexwidth}} {printable}')

    if show:
        for line in results:
            print(line)
    else:
        return results

def receive_from(connection):
    # 接收本地或远程数据, 先传入一个socket对象
    buffer = b''
    # 设置超时时间5秒
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer

def request_handler(buffer):
    # 修改请求的数据包
    return buffer

def response_handler(buffer):
    # 修改回复的数据包
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # 连接远程主机
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        # 确认是否需要先从服务器接收数据
        # 例如FTP服务器需要先接收欢迎信息后才能发送数据给它
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)

    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." %len(remote_buffer))
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print("[<==] Received %d bytes from localhost." % len(local_buffer))
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            
            remote_socket.send(local_buffer)
            print("[<==] Send to remote.")
        
        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print("[<==] Receive %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)

            client_socket.send(remote_buffer)
            print("[<==] Send to localhost.")

        if not len(remote_buffer) or not len(local_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    # 创建和管理连接
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print("problem on bind: %r" % e)
        print("[!!] Fail to listen on %s: %d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print("Received incoming connection from %s:%d" %(addr[0], addr[1]))

         # 每出现一个新的连接, 新开一个线程并交给proxy_handler函数
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./tcp-proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./tcp-proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


if __name__ == '__main__':
    main()

# 需要管理员或root权限才能启动监听21端口
# python3 proxy.py 192.168.15.128 21 ftp.sun.ac.za 21 True

# 另一终端建立ftp会话, 连接到kali虚拟机的默认ftp端口
# ftp 192.168.15.128 