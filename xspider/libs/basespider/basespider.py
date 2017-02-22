#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 2017-02-21
# Project: basespider

import json
import time
import socket
import requests
import traceback
from requests.exceptions import ReadTimeout
from requests.exceptions import ConnectionError


class BaseGenerator(object):
    """
    BaseSpider Generator
    """

    def __init__(self):
        """
        Generator Initialization
        """
        self.urls = []

    def generate(self, url):
        """
        Obtain URI
        :return:
        """
        self.urls.append(url)

        for url in self.urls:
            print json.dumps({"url": url, "args": 'None'})

    def start_generator(self):
        """
        Start Generator
        :return:
        """
        start_url = "__START_URL__"
        self.generate(start_url)


class BaseDownloader(object):
    """
    BaseSpider Downloader
    """

    def __init__(self):
        """
        Downloader Initialization
        """
        self.reqst = requests.Session()
        self.headers =
            {'Accept': 'text/html, application/xhtml+xml, */*',
             'Accept-Encoding': 'gzip, deflate',
             'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
             'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'}

    def download(self, url, tools="request", timeout=50, **kwargs):
        """
        Downloader Download By Type
        :return: response object
        """
        if tools == "request":
            start_time = time.time()
            try:
                resp = self.reqst.get(url, timeout=timeout, **kwargs)
                if resp.status_code != 200:
                    resp = self.reqst.get(url, timeout=50)
                    if resp.status_code != 200:
                        raise ConnectionError
                end_time = time.time()
                return resp

            except Exception:
                print traceback.format_exc()


class BaseParser(object):
    """
    BaseSpider Parser
    """

    def __init__(self):
        """
        Parser Initialization
        """
        pass

    def parser(self, resp):
        """
        Paeser resp content
        :param resp:
        :return:
        """
        return resp


