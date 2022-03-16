#!/usr/bin/env python

import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from time import sleep

def request(url):
    try:
        s = requests.Session()
        s.keep_alive = False
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        response = requests.get('http://'+ url)
        return response
    except (requests.exceptions.ConnectionError,requests.exceptions.TooManyRedirects, requests.exceptions.SSLError):
        # print("[+] Sleep.")
        sleep(5)

def crawl_subdomain(target_url, subdomain_dict):
    discovered_url = ""
    with open(subdomain_dict, "r") as wordlist_file:
        # content = wordlist_file.read()
        for line in wordlist_file:
            # strip \n
            subdomain = line.strip()
            test_url = subdomain + "." + target_url
            try:
                response = request(test_url)
            except requests.exceptions.TooManyRedirects and requests.exceptions.InvalidURL:
                pass
            if response:
                print("[+] Discovered subdomain --> " + test_url)
                discovered_url += test_url
    return discovered_url

def crawl_dir(target_url, file_dict):
    discovered_dir = ""
    with open(file_dict, "r") as wordlist_file:
        for line in wordlist_file:
            word = line.strip()
            test_dir = target_url + "/" + word
            response = request(test_dir)
            if response:
                print("[+] Discovered URL --> " + test_dir)
                discovered_dir += test_dir
    return discovered_dir

def write_to_file(content, filename):
    with open(filename, "w")as file:
        file.write(content)


target_url = "google.com"
discovered_url = crawl_subdomain(target_url, "subdomains-wordlist.txt")
write_to_file(discovered_url, "result.txt")
discovered_file = crawl_dir(target_url, "files-and-dirs-wordlist.txt")