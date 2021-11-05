# netdiscover -r [ip range]
# route -n: router ip

#!/usr/bin/env python

import scapy.all as scapy
import argparse

def get_arguments():
    #optparse works for python2,3; argparse for 3
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target", help="target ip range to scan")
    options = parser.parse_args()

    if not options.target:
        print("[-] Please specify an target of ip range, use --help for more info.")
    return options

def scan(ip):
    arp_request = scapy.ARP(pdst = ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request

    # scapy.ls() gives info of names, variables, default value, e.g. scapy.ls(scapy.ARP())
    # print(arp_request.summary()), e.g. ARP who has [ip] says (ip)
    # print(broadcast.summary()), e.g. [MAC] > ff:ff:ff:ff:ff:ff (0x9000)
    # --> arp_request_broadcast.show(), gives detailed information

    # scapy.sr():send & receive, srp():allow for a customed Ether package, need to configure Ether dst first
    # return a couple of two lists: answered(packet sent, answer) & unanswered
    # timeout if do not get an answer in 1s, verbose=False shows less info
    answered_list, unanswered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)
    
    # create a list of dict
    clients_list = []
    for element in answered_list:
        # print(element[1].show()), psrc: src ip, hwsrc: src mac
        client_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
        clients_list.append(client_dict)
    return clients_list

def print_result(results_list):
    print("IP\t\t\tMAC Address\n----------------------------------------")
    for client in results_list:
        print(client["ip"] + "\t\t" + client["mac"])
    print("Scan finished.")

options = get_arguments()
scan_result = scan(options.target)
if scan_result:
    print_result(scan_result)