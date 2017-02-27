#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 2017-02-21
# Project: basespider

import json
import time
import socket
import requests
import traceback
from pyquery import PyQuery
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
        pass

    def generate(self, url):
        """
        Obtain URI
        :return:
        """
        return {"url": url, "args": {}}

    def start_generator(self):
        """
        Start Generator
        :return:
        """
        start_url = "__START_URL__"
        result = self.generate(start_url)
        return result


class BaseDownloader(object):
    """
    BaseSpider Downloader
    """

    def __init__(self):
        """
        Downloader Initialization
        """
        pass

    def download(self, url, args={}, tools='requests', method='GET'):
        """
        Downloader Download By tools
        :return: response object
        """
        if isinstance(args, basestring):
            args = json.loads(args)
        if tools == "requests":
            self.reqst = requests.Session()
            self.headers = {'Accept': 'text/html, application/xhtml+xml, */*',
             'Accept-Encoding': 'gzip, deflate',
             'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
             'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:39.0) Gecko/20100101 Firefox/39.0'}
            kwargs = {
                'headers': args.get('headers', self.headers),
                'cookies': args.get('cookies', None),
                'proxies': args.get('proxies', None),
                'timeout': args.get('timeout', 30)}
            if str(method).upper() == 'GET':
                kwargs['params'] = args.get('params', {})
            elif str(method).upper() == 'POST':
                kwargs['data'] = args.get('data', {})
            try:
                resp = self.reqst.request(method=method, url=url, **kwargs)
                resp.doc = PyQuery(resp.content)
                return resp
            except Exception:
                print traceback.format_exc()
                raise Exception

        elif tools == 'js':
            """
            Download by Phantomjs
            """
            # TODO
            pass


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


