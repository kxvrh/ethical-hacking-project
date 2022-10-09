import socket
import os

# host to listen on, 设置为本机
HOST = '192.168.15.1'

def main():
    # create raw socket, bin to public interface
    if os.name == 'nt':
        # windows允许嗅探任何协议的所有流入数据
        socket_protocol = socket.IPPROTO_IP
    else:
        # linux强制指定嗅探某种协议
        socket_protocol = socket.IPPROTO_ICMP

    # 构建socket, 传入嗅探网卡数据所需的参数
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    # 端口0为通配符, 系统分配一个空闲端口 --> 指定动态生成的端口
    sniffer.bind((HOST, 0))

    # 修改设置, 使得抓包时包含IP头
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # 通过socket输入/输出控制(IOCTL)设定标志, 网卡启动混杂模式
    # IOCTL是用户程序和系统内核组件通信的一种方式
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    
    print(sniffer.recvfrom(65565))

    # 若为windows, 网卡关闭混杂模式
    if os.name =='nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

if __name__ == '__main__':
    main()