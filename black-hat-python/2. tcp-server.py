import socket
import threading


IP = '192.168.15.128'
PORT = 5555

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 指定监听的IP和端口
    server.bind((IP, PORT))
    # 开始监听, 最大连接数设置为5
    server.listen(5)
    print(f'[*] Listening on {IP}:{PORT}')

    while True:
        # 当某一客户端成功连接时, 将客户端socket对象保存在client, 远程连接信息保存在address
        client, address = server.accept()

        print(f'[*] Accpeted connection from {address[0]}:{address[1]}')

        # 创建一个新的线程, 指向handle_client函数, 传入client变量
        client_handler = threading.Thread(target=handle_client, args=(client, ))
        # 启动线程处理收到的连接
        client_handler.start()

        # 主循环准备好处理下一个外来连接

def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b'ACK')

if __name__ == '__main__':
    main()