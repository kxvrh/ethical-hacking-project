#!/usr/bin/env python

# ifconfig wlan0 down
# ifconfig wlan0 hw ether 00:11:22:33:44:55
# ifconfig wlan0 up

# use subprocess to execute system commands
# commands depend on the OS which executes the script
# subprocess.call() --> foreground, not another thread

import subprocess
import optparse
import re

def get_arguments():
    # input: python3, raw_input: python2.7
    # interface = input("interface > ")
    # new_mac = input("new MAC > ")

    parser = optparse.OptionParser()

    #store result in dest
    parser.add_option("-i", "--interface", dest="interface", help="Interface to change its MAC address")
    parser.add_option("-m", "--mac", dest="new_mac", help="New MAC address")
        
    #options: input, arguments: -i, -m
    (options, arguments) = parser.parse_args()
    if not options.interface:
        parser.error("[-] Please specify an Interface, use --help for more info.")
    elif not options.new_mac:
        parser.error("[-] Please specify a new mac, use --help for more info.")
    return options


def change_mac(interface, new_mac):
    # input can be hijacked, e.g. wlan0; ls;
    # subprocess.call("ifconfig " + interface + " down", shell=True)
    # subprocess.call("ifconfig " + interface + " hw ether " + new_mac, shell=True)
    # subprocess.call("ifconfig " + interface + " up", shell=True)
    # subprocess.call("ifconfig" + interface, shell=True)

    # separate input with space --> become parameters, no need adding space to form a string
    subprocess.call(["ifconfig", interface, "down"])
    subprocess.call(["ifconfig", interface, "hw", "ether", new_mac])
    subprocess.call(["ifconfig", interface, "up"])

    print("[+] Changing MAC address for " + interface + " to " + new_mac)
    
def get_current_mac(interface):
    #capture the result of commands
    ifconfig_result = subprocess.check_output(["ifconfig", interface])

    # r"PATTERN", \w: 0-9a-zA-Z, return all-matched object --> group 0,1,...
    # python3 distinguishes string & byte-like object, need to be casted
    mac_address_search_result = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", str(ifconfig_result))
    if(mac_address_search_result):
        return mac_address_search_result.group(0)
    else:
        # return NoneType, need to be casted to str
        print("[-] Could not read MAC address.")

options = get_arguments()

current_mac = get_current_mac(options.interface)
print("Current MAC = " + str(current_mac))

change_mac(options.interface, options.new_mac)

current_mac = get_current_mac(options.interface)
if current_mac == options.new_mac:
    print("[+] MAC address was successfully changed to " + current_mac)
else:
    print("[-] MAC address did not get changed.")