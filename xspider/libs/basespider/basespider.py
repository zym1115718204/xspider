#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 2017-02-21
# Project: basespider

import json
import time
import socket
import random
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
    def generate(url, callback=None, args=None):
        """
        Obtain URI
        :return:
        """
        return {"url": url, "args": args if args else {}, "callback": callback.__name__}

    def download(self, url, args={}):
        """
        Downloader Download By tools
        :return: response object
        """
        if isinstance(args, basestring):
            args = json.loads(args)
        tools = args.get('tools', 'requests')
        method = args.get('method', 'GET')
        if tools == "requests":
            self.reqst = requests.Session()
            self.headers = {'Accept': 'text/html, application/xhtml+xml, */*',
             'Accept-Encoding': 'gzip, deflate',
             'Accept-Language': 'en-US, en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
             'User-Agent': self.get_user_agent()}
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
            resp = self.reqst.request(method=method, url=url, verify=False, **kwargs)
            if resp.status_code != 200:
                raise ConnectionError("ConnectionError, {0}".format(resp.status_code))
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
    def get_user_agent():
        agents = [
            "msnbot-media/1.1 (+http://search.msn.com/msnbot.htm)",
            "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Sosospider+(+http://help.soso.com/webspider.htm)",
            "Sosoimagespider+(+http://help.soso.com/soso-image-spider.htm)",
            "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)",
            "Mozilla/5.0 (compatible; Yahoo! Slurp China; http://misc.yahoo.com.cn/help.html)",
            "http://pic.sogou.com” “Sogou Pic Spider/3.0(+http://www.sogou.com/docs/help/webmasters.htm#07)",
            "Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "AdsBot-Google-Mobile (+http://www.google.com/mobile/adsbot.html) Mozilla (iPhone; U; CPU iPhone OS 3 0 like Mac OS X) AppleWebKit (KHTML, like Gecko) Mobile Safari",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0); 360Spider",
            "Mozilla/5.0 (compatible; YoudaoBot/1.0; http://www.youdao.com/help/webmaster/spider/; )",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) Speedy Spider (http://www.entireweb.com/about/search_tech/speedy_spider/)",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "Mozilla/5.0 (compatible; EasouSpider; +http://www.easou.com/search/spider.html)",
            "HuaweiSymantecSpider/1.0+DSE-support@huaweisymantec.com+(compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR ; http://www.huaweisymantec.com/cn/IRL/spider)",
            "qiniu-imgstg-spider-1.0",
            "xFruits/1.0 (http://www.xfruits.com)",
            "Feedly/1.0 (+http://www.feedly.com/fetcher.html; like FeedFetcher-Google)",
            "Mozilla/5.0 (compatible;YoudaoFeedFetcher/1.0;http://www.youdao.com/help/reader/faq/topic006/;1 subscribers;)",
            "FeedDemon/4.5 (http://www.feeddemon.com/; Microsoft Windows)",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; JianKongBao Monitor 1.1)",
            "Mozilla 5.0 (compatible; Feedsky crawler /1.0; http://www.feedsky.com)",
            "Xianguo.com 1 Subscribers",
            "360spider(http://webscan.360.cn)",
            "yrspider Mozilla/5.0 (compatible; YRSpider; +http://www.yunrang.com/yrspider.html)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; EmbeddedWB 14.52 from: http://www.bsalsa.com/ EmbeddedWB 14.52; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 6.0; AugustBot/augstbot@163.com)",
            "Mozilla/5.0 (compatible; DotBot/1.1; http://www.dotnetdotcom.org/, crawler@dotnetdotcom.org)",
            "Mozilla/5.0 (compatible; DotBot/1.1; http://www.opensiteexplorer.org/dotbot, help@moz.com)",
            "http://www.internet-zarabotok.net/” “Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; Win64; AMD64)",

            "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html）",
            "Mozilla/5.0 (Linux;u;Android 4.2.2;zh-cn;)AppleWebKit/534.46 (KHTML,like Gecko) Version/5.1 Mobile Safari/10600.6.3 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html）",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 6.0.1; ALCATEL ONETOUCH POP? 7 LTE Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.91 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 6.0.1; en-us;ALCATEL ONETOUCH POP 7 LTE Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/42.0.2311.154 Mobile Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.2; rv:40.0) Gecko/20100101 Firefox/40.0",
            "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.2 (KHTML, like Gecko) Ubuntu/11.10 Chromium/15.0.874.120 Chrome/15.0.874.120 Safari/535.2",
            "Mozilla/5.0 (X11; Linux i686; rv:28.0) Gecko/20100101 Firefox/28.0",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler ; EmbeddedWB 14.52 from: http://www.bsalsa.com/ EmbeddedWB 14.52; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30; .N  •   Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 6.0.1; ALCATEL ONETOUCH POP? 7 LTE Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.91 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 6.0.1; en-us;ALCATEL ONETOUCH POP 7 LTE Build/MMB29M) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/42.0.2311.154 Mobile Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.2; rv:40.0) Gecko/20100101 Firefox/40.0",
            "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.2 (KHTML, like Gecko) Ubuntu/11.10 Chromium/15.0.874.120 Chrome/15.0.874.120 Safari/535.2",
            "Mozilla/5.0 (X11; Linux i686; rv:28.0) Gecko/20100101 Firefox/28.0",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler ; EmbeddedWB 14.52 from: http://www.bsalsa.com/ EmbeddedWB 14.52; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30; .NET CLR 3.0.04506.590; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            "Mozilla/5.0 (compatible; proximic; +http://www.proximic.com/info/spider.php)",
            "Mozilla/5.0 (X11; Linux i686; rv:28.0) Gecko/20100101 Firefox/28.0",
            "Mozilla/5.0 (compatible; NetSeer crawler/2.0; +http://www.netseer.com/crawler.html; crawler@netseer.com)",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.16) Gecko/20080716 (Gentoo) Galeon/2.0.6",
            "Mozilla/5.0 (X11; Linux i686; rv:14.0) Gecko/20100101 Firefox/14.0.1 Iceweasel/14.0.1",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            "ET CLR 3.0.04506.590; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            "Mozilla/5.0 (compatible; proximic; +http://www.proximic.com/info/spider.php)",
            "Mozilla/5.0 (X11; Linux i686; rv:28.0) Gecko/20100101 Firefox/28.0",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.16) Gecko/20080716 (Gentoo) Galeon/2.0.6",
            "Mozilla/5.0 (X11; Linux i686; rv:14.0) Gecko/20100101 Firefox/14.0.1 Iceweasel/14.0.1",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        ]
        return random.choice(agents)


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



