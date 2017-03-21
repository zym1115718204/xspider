#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 2017-03-09 05:29:39
# Project: guangdong

from bs4 import BeautifulSoup
from libs.basespider.basespider import *
from libs.basicgeetestcrack import IndustryAndCommerceGeetestCrack
from urllib import unquote
from requests.models import Response
from pyquery import PyQuery
import urlparse

class Spider(BaseSpider):
    """
    Spider Generator
    """

    def start_generator(self):
        """
        Start Generator
        :return: URL List
        :example: [{"url":"http://www.example.com", "args":None, "callback":"parser_detail"}]
        """
        result = []

        start_url = u'http://gd.gsxt.gov.cn?args=中国移动'.encode('utf8')
        result_url = self.generate(start_url, callback=self.parser_index)
        result.append(result_url)

        return result

    def start_downloader(self, url, args):
        """
        Start Downloader
        """
        resp = Response()
        if url.find(u'?args=') > -1:
            real_url, search_word = url.split('?args=')
            search_word = unicode(unquote(search_word))
            print 'url: ', real_url
            print 'search_word: ', search_word
            c = IndustryAndCommerceGeetestCrack(
                url=real_url,
                search_text=search_word,
                input_id="content",
                search_element_id="search",
                gt_element_class_name="gt_box",
                gt_slider_knob_name="gt_slider_knob",
                result_numbers_xpath='/html/body/div[1]/div[6]/div[1]/span',
                result_list_verify_class='clickStyle')
            result, cookies = c.crack()
            current_url = real_url
            body = result.encode('utf-8') if result else u'<html>有异常出现了</html>'.encode('utf-8')
            # resp.status_code = 200
            resp._content = body
            resp.url = real_url
            resp.doc = PyQuery(body)
            return resp
        else:
            resp = self.download(url, args=args)
            return resp

    def start_parser(self, response, callback):
        """
        Start Parser
        """
        result = callback(response)

        return result

    def parser_index(self, response):
        """
        Parser Index Page to Result
        :param response:
        :return: dict
        """
        urls = []
        host = 'http://gd.gsxt.gov.cn/aiccips/CheckEntContext/showCheck.html'
        soup = BeautifulSoup(response.content, 'html.parser')
        divs = soup.find_all('div', attrs={'class': 'clickStyle'})
        for div in divs:
            next_url = div.find('a')['href'] if div.find('a') else None
            print 'next_url: ', next_url
            if next_url:
                _url = self.generate(urlparse.urljoin(host, next_url), 
                                        args={'tools': 'phantomjs'}, 
                                        callback=self.parser_item)
                urls.append(_url)
        # for each in response.doc('a[href^="http"]').items():
        #     _url = self.generate(each.attr.href, callback=self.parser_detail)
        #     urls.append(_url)

        result = {
            "urls": urls
        }
        return result

    def parser_item(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        result = {
            'url': response.url,
            'title': response.doc('title').text()
        }
        result['ind_comm_pub_reg_basic'] = self.parser_ind_comm_pub_reg_basic(self, soup)
        
        yield result

        # yield {
        #     'encode': response.xpath('/html/body/div[1]/div[6]/div[5]/div[2]/div[1]/table/tbody/tr[2]/td[1]').extract_first(),
        #     'name': response.xpath('/html/body/div[1]/div[6]/div[5]/div[2]/div[1]/table/tbody/tr[2]/td[2]').extract_first(),
        #     'type': response.xpath('/html/body/div[1]/div[6]/div[5]/div[2]/div[1]/table/tbody/tr[3]/td[1]').extract_first(),
        #     'eare': response.xpath('/html/body/div[1]/div[6]/div[5]/div[2]/div[1]/table/tbody/tr[9]/td').extract_first()
        # }

    def parser_ind_comm_pub_reg_basic(self, soup):
        temp_dict = {}
        div = soup.find('div', attrs={'class': 'infoStyle'})
        if div:
            tds = div.find('table').find_all('td')[1:]
            for td in tds:
                key, value = td.get_text().strip()[1:].split(u'：', 1)
                print key.strip(), value.strip()
                temp_dict[key.strip()] = value.strip()

        else:
            pass
        return temp_dict


    # def parser_item(self, response):
    #     """
    #     Parser Detail Page to Result
    #     :param response:
    #     :return: dict
    #     """
    #     print '--------' * 20
    #     print response.content
    #     result = {
    #         "url": response.url,
    #         "title": response.doc('title').text(),
    #         "body": response.content
    #     }
    #     return result