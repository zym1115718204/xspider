#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on __CREATE_TIME__
# Project: __PROJECTS_NAME__

import json
import time
import socket
import requests
import traceback
from requests.exceptions import ReadTimeout
from requests.exceptions import ConnectionError


class Generator(object):
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
            print json.dumps({"url":url, "args": 'None'})

    def start_generator(self):
        """
        Start Generator
        :return:
        """
        start_url = "__START_URL__"
        self.generate(start_url)


class Downloader(object):
    """
    BaseSpider Downloader
    """

    def __init__(self):
        """
        Downloader Initialization
        """
        self.reqst = requests.Session()
        self.reqst.headers.update(
            {'Accept': 'text/html, application/xhtml+xml, */*',
             'Accept-Encoding': 'gzip, deflate',
             'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
             'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'})

    def download(self, url, type="request", timeout=50):
        """
        Downloader Download By Type
        :return: response object
        """
        if type == "request":
            start_time = time.time()
            try:
                resp = self.reqst.get(url, timeout=timeout)
                if resp.status_code != 200:
                    resp = self.reqst.get(url, timeout=50)
                    if resp.status_code != 200:
                        raise ConnectionError
                end_time = time.time()
                return resp

            except Exception:
                print traceback.format_exc()


class Parser(object):
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


