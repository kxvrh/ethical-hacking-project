#!/usr/bin/env python

import requests
import re
# import urlparse
import urllib.parse as urlparse

class Spider:
    def __init__(self, url):
        self.target_links = []
        self.target_url = url

    def write_to_file(self, content, filename):
        with open(filename, "w")as file:
            file.write(content)

    def download_file(self, url, path):
        get_response = requests.get(url)
        filename = path + url.split("/")[-1]

        with open(filename, mode="wb") as out_file:
            out_file.write(get_response.content)
        print("[+] Download sucessfully.")

    def extract_link_from(self, url=None):
        if url == None:
            url = self.target_url
        response = requests.get(url, verify=False)
        # (.*?): non-greedy, find the first next "
        # href_links = re.findall('(?:href=")(.*?)"', str(response.content))
        href_links = re.findall('(?:href=")(.*?)"', response.content.decode(errors="ignore"))
        return href_links

    def crawl_links(self, url=None):
        if url == None:
            url = self.target_url
        href_links = self.extract_link_from(url)
        for link in href_links:
            # convert relative url to full url
            link = urlparse.urljoin(url, link)

            if "#" in link:
                # to get unique link
                link = link.split("#")[0]

            if self.target_url in link and link not in self.target_links:
                self.target_links.append(link)
                print(link)

                # recursive search
                self.crawl_links(link)

    def extract_pictures_from(self, url=None):
        if url == None:
            url = self.target_url
        response = requests.get(url)
        img_src_links = re.findall('(?:img src=")(.*?)"', str(response.content))
        return img_src_links

    def crawl_pictures(self, url=None):
        if url == None:
            url = self.target_url
        pic_links = self.extract_pictures_from(url)
        for link in pic_links:
            link =  urlparse.urljoin(url, link)
            print(link)


target_url = "http://www.speedbit.com/"
try:
    my_spider = Spider(target_url)
    my_spider.crawl_links()
    # my_spider.crawl_pictures()
except KeyboardInterrupt:
    exit()
