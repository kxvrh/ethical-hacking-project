#!/usr/bin/env python

import requests
import optparse

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-u", "--url", dest="url", help="Download URL.")
    options, arguments = parser.parse_args()
    if not options.url:
        parser.error("[-] Please specify the url to download file.")
    return options

def download(url):
    # GET request --> response
    get_response = requests.get(url)

    # splited by /, last element is the filename
    filename = url.split("/")[-1]

    with open(filename, mode="wb") as out_file:
        # open a binary file to write
        out_file.write(get_response.content)
    print("[+] Download sucessfully.")
        
options = get_arguments()
download(options.url)