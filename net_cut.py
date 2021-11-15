#!/usr/bin/env python

import netfilterqueue
import subprocess
import optparse

def modify_iptables(queue_num):
    # iptables -I FORWARD -j NFQUEUE --queue-num 0
    # modify iptables to trap all packets that usually go to FORWARD chain in NetFilterQueue(0)
    # pip install netfilterqueue
    # request from/to host computer --> OUTPUT/INPUT, from other computer --> FORWARD
    subprocess.call(["iptables -I OUTPUT -j NFQUEUE --queue-num ", queue_num])
    subprocess.call(["iptables -I INPUT -j NFQUEUE --queue-num ", queue_num])
    # subprocess.call(["iptables -I FORWARD -j NFQUEUE --queue-num ", queue_num])
    print("[+] IPtables modified ... Packet trap in queue " + str(queue_num))

def restore_iptables():
    subprocess.call("iptables --flush")
    print("[+] IPtables restored.")

def process_packet(packet):
    print(packet)

    # packet.accept() --> forwarding packet to its destination
    packet.drop()

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-n", "--queue_num", dest="queue_num", help="NFQueue number.")
    options, arguments = parser.parse_args()
    if not options.queue_num:
        parser.error("[-] Please specify a queue number, use --help for more info.")
    return options

options = get_arguments()
modify_iptables(options.queue_num)
queue = netfilterqueue.NetFilterQueue()
queue.bind(options.queue_num, process_packet)
try:
    queue.run()
except KeyboardInterrupt:
    restore_iptables()