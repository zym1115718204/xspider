#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 2017-03-2
# Project: Result_dump


import six
import csv
import time
import json
import codecs
from collector.models import Project


class ResultDump(object):
    """
    Result Module
    """

    def __init__(self, project):
        """
        Initialization
        """
        self.project = project

    def dump(self):
        """
        Result_dump
        :return:
        """
        data = []
        total = 0
        result = []
        start = time.time()
        _name = str(self.project.name)
        exec("from execute.{0}_models import {1}Result".format(_name, _name.capitalize()))
        exec("total = {0}Result.objects().count()".format(_name.capitalize()))
        exec("data = {0}Result.objects()".format(_name.capitalize()))

        for _data in data:
            _result = json.loads(_data["result"])
            # _result = _data["result"]
            # for k,v in _result.iteritems():
            #     print k,v
            result.append(_result)

        return {
            "project": _name,
            "data": result,
            "total": total,
            "status": True,
            "spend_time": time.time()-start
        }

    def dump_as_json(self):
        """
        Dump as Json
        :return:
        """
        result = self.dump()
        return json.dumps(result)

    def dump_as_csv(self):
        """
        Dump CSV
        :return:
        """
        result = self.dump()
        rows = []
        headers = []
        for data in result.get("data", []):
            if not headers:
                for key in data.iterkeys():
                    headers.append(key)
            rows.append(data)

        # import unicodecsv as csv
        # from io import BytesIO
        # f = BytesIO()
        #
        # w = csv.writer(f, encoding='utf-8')
        # _ = w.writerow((u'é', u'ñ'))
        # _ = f.seek(0)
        #
        # r = csv.reader(f, encoding='utf-8')
        # next(r) == [u'é', u'ñ']

        # headers = [u'url', u'title']
        # rows = [{u'url': u"www.baidu.com", u'title': u"title"}]

        print rows
        if not rows:
            return json.dumps({
                "status": False,
                "reason": "Project data does exists!"
            })
        else:
            with codecs.open('stocks.csv', 'w', 'UTF-8') as f:
                for header in headers:
                    f.write(header + ',')
                f.write('\n')

                for line in rows:
                    for value in line.itervalues():
                        f.write(value+',')
                    f.write('\n')

            return json.dumps({
                "status": True
            })







