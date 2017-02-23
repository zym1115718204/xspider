#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.23

import json
from collector.models import Project
from django.conf import settings


class Manager (object):

    def __init__(self, ip='127.0.0.1', project_name=None):
        """
        :param ip:
        :param project_name:
        """
        self.ip = ip
        self.project_name = project_name
        self.redis_url = settings.REDIS_URL

    def do_alanysis_with_redis(self, target_dict=None, reference_dict=None):
        """
        :param target_dict:
        :param reference_dict:
        :return: a_json_str
        """
        if target_dict:
            is_granted, ip_port = True, '127.0.0.1'
        else:
            is_granted, ip_port = False, '0.0.0.0'
        return json.dump({
            'granted': is_granted,
            'local_ip': self.ip,
            'proxies_ip': ip_port,
            'count': 1
        })

    def get_target_dict(self):
        """
        :return: a_dict
        """

        try:
            one_project = Project.objects.filter(name=self.project_name).first()
            print 'one_project.name: ', one_project.name
        except Exception as e:
            print (u'数据库查询出错了, %s project可能并不存在mongodb。' % (self.project_name))
            raise e
        if one_project is None:
            print (u'数据库查询出错了, %s project可能并不存在mongodb。' % (self.project_name))
            raise ValueError

        target_dict = {
            'name': one_project.name,
            'ip': self.ip,
            'generator_interval': one_project.generator_interval,
            'downloader_interval': one_project.downloader_interval,
            'downloader_dispatch': one_project.downloader_dispatch
        }
        return target_dict

    def get_reference_dict(self):
        """
        :return: a_dict
        """

        # 连接 redis
        # 得到 redis[key=project_name])
        # 返回
        reference_dict = {}
        return reference_dict

    def get_ip(self):
        """
        :return: str that json.dump
        """
        # TODO:
            # 与 redis里的ip使用情况作对比

        target_dict = self.get_target_dict()
        reference_dict = self.get_reference_dict()
        result = self.do_alanysis_with_redis(reference_dict=reference_dict,
                                             target_dict=target_dict)
        return result

