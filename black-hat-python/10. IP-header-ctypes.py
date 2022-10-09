from ctypes import *
import socket
import struct

class IP(Structure):    
    # 创建对象前必须定义_fields_结构
    _fields_ = [                                # 创建_fields_结构定义IP头的各个部分(字段名称, 数据类型, 字段位数)
        ("ihl",             c_ubyte, 4),        # 4 bit unsigned char   头长度
        ("version",         c_ubyte, 4),        #                       版本
        ("tos",             c_byte, 8),         # 1 byte char           服务类型
        ("len",             c_ushort, 16),      # 2 byte unsigned short 总长度
        ("id",              c_ushort, 16),      #                       标识
        ("offset",          c_ushort, 16),      #                       段偏移
        ("ttl",             c_ubyte, 8),        # 1 byte char           生存时间TTL
        ("protocol_num",    c_ubyte, 8),        #                       协议号
        ("sum",             c_ushort, 16),      # 2 byte unsigned short 头校验和
        ("src",             c_uint32, 32),      # 4 byte unsigned int   源IP地址
        ("dst",             c_uint32, 32)       #                       目的IP地址
    ]

    def __new__(cls, socket_buffer=None):
        # 为了向_fields_结构填充数据, 底层解释器会调用__new__, 将数据填入_fields_, 再传给__init__
        # cls为一个指向当前类的引用, __new__函数会用这个应用创建当前类的一个对象, 并将该对象传给__init__进行初始化
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        # readable IP address
        self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))
