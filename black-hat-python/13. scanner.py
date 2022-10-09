import ipaddress
import struct
import os
import sys
import socket
import threading
import time

SUBNET = '10.40.0.0/22'
# 定义一个简单的字符串作为"签名", 用于确认收到的ICMP响应是否是由我们发出的UDP包所触发的
MESSAGE = 'HELLOO'

class IP:
    def __init__(self, buff=None):
        # <表示数据的字节序 --> kali(x64系统)为小端序(little-endian) --> 低位字节存在放较低的内存地址
        # B为1字节(unsigned char), H为2字节(unsigned short), s为一个字节数组, 数组长度需要另外指定
        header = struct.unpack('<BBHHHBBH4s4s', buff)

        self.ver = header[0] >> 4       # 第一个字节的高位nybble(4个二进制位的数据块) --> 右移4位
        self.ihl = header[0] & 0xF      # 第一个字节的低位nybble(原字节最后4个二进制) --> 与0xF(00001111)按位与
        self.tos = header[1]
        self.len = header[2]
        self.id  = header[3]
        self.offset = header[4]
        self.ttl = header[5]
        self.protocol_num = header[6]
        self.sum = header[7]
        self.src = header[8]            # 4字节的字节数组
        self.dst = header[9]

        # readable IP address
        self.src_address = ipaddress.ip_address(self.src)
        self.dst_address = ipaddress.ip_address(self.dst)

        self.procotol_map = {1: "IMCP", 6: "TCP", 17:"UDP"}

        try:
            self.protocol = self.procotol_map[self.protocol_num]
        except Exception as e:
            print('%s No protocol for %s' % (e, self.protocol_num))
            self.protocol = str(self.protocol_num)

class ICMP:
    def __init__(self, buff=None):
        header = struct.unpack(">BBHHH", buff)
        self.type = header[0]       # 1字节的类型
        self.code = header[1]       # 1字节的代码
        self.sum  = header[2]       # 2字节的头校验和
        self.id   = header[3]       # 
        self.seq  = header[4]

def udp_sneder():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM)as sender:
        for ip in ipaddress.ip_network(SUBNET).hosts():
            # 向子网中每一个地址发送UDP包
            # 自定义8字节特征数据放在UDP数据包开头
            sender.sendto(bytes(MESSAGE, 'utf8'), (str(ip), 65212))

class Scanner:
    def __init__(self, host):
        if os.name == 'nt':
            # windows允许嗅探任何协议的所有流入数据
            socket_protocol = socket.IPPROTO_IP
        else:
            # linux强制指定嗅探某种协议
            # 仅能看到ICMP响应包
            socket_protocol = socket.IPPROTO_ICMP

        # 构建socket, 传入嗅探网卡数据所需的参数
        self.sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
        # 端口0为通配符, 系统分配一个空闲端口 --> 指定动态生成的端口
        self.sniffer.bind((host, 9999))
        # 修改设置, 使得抓包时包含IP头
        self.sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        # 通过socket输入/输出控制(IOCTL)设定标志, 网卡启动混杂模式
        if os.name == 'nt':
            self.sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    
    def sniff(self):
        hosts_up = set([f':{str(self.host)}*'])
        try:
            while True:
                raw_buffer = self.sniffer.recvfrom(65535)[0]
                # 每读入一个包, 将前20字节转换成IP头对象
                ip_header = IP(raw_buffer[0:20])

                if ip_header.protocol == "ICMP":
                    print('Protocol: %s %s -> %s' % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))
                    print(f'Version: {ip_header.ver}')
                    print(f'Header Length: {ip_header.ihl}  TTL: {ip_header.ttl}')
                    
                    # 计算icmp开始的偏移量
                    offset = ip_header.ihl * 4
                    buf = raw_buffer[offset: offset + 8]
                    icmp_header = ICMP(buf)
                    print('ICMP -> Type: %s Code: %s\n' %(icmp_header.type, icmp_header.code))

                    if icmp_header.type == 3 and icmp_header.code == 3:
                        # 检查该响应是否来自于扫描的子网
                        if ipaddress.ip_address(ip_header.src_address) in ipaddress.IPv4Address(SUBNET):
                            # 检查该响应里是否包含自定义的签名
                            # ICMP相应包会将触发该响应的原始数据包IP头附在消息末尾 --> 最后8字节
                            if raw_buffer[len(raw_buffer) - len(MESSAGE):] == bytes(MESSAGE, 'utf8'):
                                tgt = str(ip_header.src_address)
                                hosts_up.add(str(ip_header.src_address))
                                print(f'Host Up: {tgt}')

        except KeyboardInterrupt:
            # 若为windows, 网卡关闭混杂模式
            if os.name == 'nt':
                self.sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
            print('\nUser interrupted.')

            if hosts_up:
                print(f'\n\nSummary: Hosts up on {SUBNET}')
                for host in sorted(hosts_up):
                    print(f'{host}')
                print('')
            sys.exit()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        host = sys.argv[1]
    else:
        host = '10.40.3.110'
    s = Scanner(host)
    time.sleep(5)
    t = threading.Thread(target=udp_sneder)
    t.start()