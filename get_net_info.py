#!/usr/bin/env python

import uuid
import socket

def get_mac_address():
    mac = uuid.UUID(int = uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0,11,2)])

def get_ip_address():
    # create a UDP which includes host IP, extract IP from the UDP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

mac = get_mac_address()
ip = get_ip_address()
print(mac, ip)