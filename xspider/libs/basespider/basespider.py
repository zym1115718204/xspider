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
from requests.models import Response
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class BaseSpider(object):
    """
    BaseSpider Generator
    """

    def __init__(self):
        """
        Generator Initialization
        """
        pass

    @staticmethod
    def generate(url, callback):
        """
        Obtain URI
        :return:
        """
        return {"url": url, "args": {}, "callback": callback.__name__}

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

            # try:
            resp = self.reqst.request(method=method, url=url, **kwargs)
            resp.doc = PyQuery(resp.content)
            return resp
            # except Exception:
            #     print traceback.format_exc()
            #     raise Exception

        elif tools == 'phantomjs':
            """
            Download by Phantomjs
            """
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap['phantomjs.page.settings.userAgent'] = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")
            # driver = webdriver.PhantomJS(desired_capabilities=dcap)  # 指定使用的浏览器
            # driver = webdriver.PhantomJS()
            driver = webdriver.Chrome()
            try:  
                print 'new get url: %s' % (url)
                driver.get(url)
                time.sleep(4)
                js = args.get('js_code', "var q=document.body.scrollTop=10000")
                driver.execute_script(js)  # 可执行js，模仿用户操作。此处为将页面拉至最底端。
                time.sleep(5)
                body = driver.page_source.encode('utf-8')
                print (u"访问" + url)
            except Exception as e:
                body = u'<html>有异常出现了</html>'.encode('utf-8')
                print str(e)
                traceback.print_exc() 
            finally:
                current_url = driver.current_url
                driver.close()
            resp = Response()
            # resp.status_code = 200
            resp._content = body
            resp.url = current_url
            resp.doc = PyQuery(body)
            return resp

    @staticmethod
    def parser(response):
        """
        Parser Response to Result
        :param response:
        :return: dict
        """
        result = {
            "url": response.url,
            "title": response.doc('title').text(),
        }
        return result

    def start_generator(self):
        """
        Start Generator
        :return: URL List
        :example: [{"url":"http://www.example.com", "args":None, "callback":"parser"}]
        """
        result = []

        start_url = "__START_URL__"
        result_url = self.generate(start_url, callback=self.parser)
        result.append(result_url)

        return result

    def start_downloader(self, url, args):
        """
        Start Downloader
        """
        resp = self.download(url, args)
        return resp

    def start_parser(self, response, callback):
        """
        Start Parser
        """
        result = callback(response)

        return result



