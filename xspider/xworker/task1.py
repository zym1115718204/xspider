from xworker import app

#app = Celery('tasks', backend='amqp', broker='amqp://guest@localhost//')
#app.config_from_object('celeryconfig')

#encoding=utf-8
""" example is http://gsxt.saic.gov.cn/
"""


import urllib
import json
import sys
import logging
import unittest
import requests
import os
import cPickle as pickle

from bs4 import BeautifulSoup
import urlparse
import pwd
import traceback
import datetime
import time


DEBUG = False
if DEBUG:
    level = logging.DEBUG
else:
    level = logging.ERROR

logging.basicConfig(level=level, format="%(levelname)s %(asctime)s %(lineno)d:: %(message)s")


class History(object):

    def __init__(self):
        self.total_page = 0
        self.current_page = 0
        self.path = "/tmp/qyxy"

    def load(self):
        if os.path.exists(self.path) is False:
            return

        with open(self.path, "r") as f:
            old = pickle.load(f)
            self.total_page = old.total_page
            self.current_page = old.current_page

    def save(self):
        with open(self.path, "w") as f:
            pickle.dump(self, f)



class Generator(object):
    def __init__(self, step=1, row=1):
        """
        source_url: http://clawer.princetechs.com/enterprise/api/get/all/?page=1&rows=10&sort=id&order=asc
        """
        self.source_url = "http://clawer.princetechs.com/enterprise/api/get/all/"
        self.step = step
        self.row = row
        self.history = History()
  #      self.history.load()
        self.enterprise_urls = []

    def obtain_enterprises(self,):
        #if self.history.current_page <= 0 and self.history.total_page <= 0:
        #    self._load_total_page()

        for _ in range(0, self.step):
            self.history.current_page += 1
            # self.history.save()
            query = urllib.urlencode({'page':self.history.current_page, 'rows': self.row, 'sort': 'id', 'order': 'asc'})
            r = requests.get(self.source_url, query)
            if r.status_code != 200:
                continue

            for item in r.json()['rows']:
                self.enterprise_urls.append(self._pack_enterprise_url(item))

            #if self.history.current_page >= self.history.total_page:
            #    self.history.current_page = 0
            #    self.history.total_page = 0
            #    self.history.save()
            #    break

    def _load_total_page(self):
        query = urllib.urlencode({'page':1, 'rows': 10, 'sort': 'id', 'order': 'asc'})
        r = requests.get(self.source_url, query)
        self.history.current_page = 0
        self.history.total_page = r.json()['total_page']
        self.history.save()

    def _pack_enterprise_url(self, row):
        return u"enterprise://localhost/%s/%s/%s/" % (row['province_name'], row['name'], row['register_no'])



class GeneratorTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def test_obtain_enterprise(self):
        self.generator = Generator()
        self.generator.obtain_enterprises()
        self.assertGreater(len(self.generator.enterprise_urls), 0)


#
# if __name__ == "__main__":
#     if DEBUG:
#         unittest.main()
#
#     generator = Generator()
#     generator.obtain_enterprises()
#     print generator.enterprise_urls

@app.task
def enterprise(step=1, row=1):
    generator = Generator(step=step,row=row)
    generator.obtain_enterprises()
    uris = generator.enterprise_urls
    uri_number= len(uris)
    add_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result={
        'uris':uris,
        "total_count": uri_number,
        'add_time': add_time
    }
    return json.dumps(result)

    # for uri in generator.enterprise_urls:
    #     print json.dumps({"uri":uri})
