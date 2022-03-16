#! usr/bin/env python

import scapy.all as scapy
import optparse

# check if arp list is modified --> cannot detect after the attack begins

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
    # arp.op = 2 --> arp response
    if packet.haslayer(scapy.ARP) and packet[scapy.ARP].op == 2:
        try:
            real_mac = get_mac(packet[scapy.ARP].psrc)
            response_mac = packet[scapy.ARP].hwsrc

            if real_mac != response_mac:
                print("[+] You are under attack!!!")
        except IndexError:
            # get own ip in get_map(ip)
            pass

def get_mac(ip):
    arp_request = scapy.ARP(pdst = ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request

    answered_list, unanswered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)
    # return only one element (packet sent, answer)
    return answered_list[0][1].hwsrc


options = get_arguments()
sniff(options.interface)