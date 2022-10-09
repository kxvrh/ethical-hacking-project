import socket

'''TCP 客户端'''

target_host = "0.0.0.0"
target_port = 9998

# 创建一个socket对象
# AF_INET表示使用标准的IPv4地址或主机名, SOCK_STREAM表示为TCP流
tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 连接
tcp_client.connect((target_host, target_port))

# 发送byte类型数据
tcp_client.send(b"abc")

# 接收返回数据
response = tcp_client.recv(4096)
print(response.decode())

tcp_client.close()


'''UDP客户端'''


target_host = "127.0.0.1"
target_port = 9999

# 创建一个socket对象
# AF_INET表示使用标准的IPv4地址或主机名, SOCK_DGRAM表示为UDP流
udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 无连接协议, 不需要connect
udp_client.sendto(b"aaabbbccc", (target_host, target_port))

# 返回数据和数据来源(主机名和端口号)
data, addr = udp_client.recvfrom(4096)
print(data.decode())

udp_client.close()