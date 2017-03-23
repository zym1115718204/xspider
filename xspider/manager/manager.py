#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.23

import json
import time
import redis
import copy
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.conf import settings
from collector.models import Project
from dashboard.handler import Handler


class Manager (object):
    """
    Xspider Nodes and Proxies Manager
    """

    def __init__(self, ip='127.0.0.1', project_name=None):
        """
        :param ip:
        :param project_name:
        """
        self.ip = ip
        self.project_name = project_name
        self.nodes = settings.NODES
        self.proxies = settings.PROXIES
        self.r = redis.Redis.from_url(settings.NODES_REDIS)

    def _add_node(self, node=None, key=None, project_name=None, is_local=False):
        """
        Add Node to Nodes
        :param node: Node IP
        :param key:
        :param project_name:
        :param is_local:
        :return:
        """
        node.update({project_name: {
            "add_time": self._get_now_timestamp(),
            "used_time": self._get_now_timestamp(),
            "refresh_time": self._get_now_timestamp(),
            "count": 1,
            "total": 1,
            "online": True
            }
        })
        if not node.has_key('status'):
            node.update({'status': True})
        if not node.has_key('is_local'):
            node.update({'is_local': is_local})
        if not node.has_key('add_time'):
            node.update({'add_time': self._get_now_timestamp()})
        self.r.hset(self.nodes, key, json.dumps(node))
        self.r.save()

    @staticmethod
    def _get_now_timestamp():
        """
        Get Current TimeStamp
        :return:
        """
        return time.time()

    def get_node(self, download_setting=None, ip=None, node=None):
        """
        Get Node from redis
        :param download_setting:
        :param node:
        :return:
        """
        iplimit = float(download_setting.get('iplimit', 1000.0))
        downloader_limit = float(download_setting.get('downloader_limit', 1000.0))
        project = node.get(self.project_name)
        status = node.get('status', True)
        online = project.get('online')
        used_time = float(project.get('used_time'))
        refresh_time = float(project.get('refresh_time'))
        count = int(project.get('count', 0))
        total = int(project.get('total', 0))
        now_time = float(self._get_now_timestamp())
        
        if status and online and used_time + iplimit <= now_time:

            if now_time - refresh_time > 3600:
                project.update({
                    'refresh_time': now_time,
                    'count': 0
                })
            if count < downloader_limit:
                project.update({
                    'used_time': now_time,
                    'count': count + 1,
                    'total': total + 1,
                })
                self.r.hset(self.nodes, ip, json.dumps(node))
                self.r.save()
                return True, ip, count+1, total+1
            else:
                return False, "0.0.0.0", count+1, total+1
        else:
            return False, '0.0.0.0', count+1, total+1

    def get_proxy(self, download_setting=None, node=None):
        """
        Get Proxy Command
        :param download_setting:
        :param node
        :return:
        """

        iplimit = float(download_setting.get('iplimit', 1000.0))
        downloader_limit = float(download_setting.get('downloader_limit', 1000.0))

        now_time = float(self._get_now_timestamp())
        count = 0
        total = 0

        for key in self.r.hgetall(self.proxies).keys():
            proxy_key = self.r.hget(self.proxies, key)
            proxy = json.loads(proxy_key) or {}
            project = proxy.get(self.project_name)

            if not project and proxy.get('status'):
                self._add_node(
                    node=proxy,
                    project_name=self.project_name,
                    key=key,
                    is_local=False
                )
                return True, key, 1, 1
            elif project and proxy.get('status'):
                # # result = self.get_node(download_setting, proxy)
                # used_time = float(proxy.get(self.project_name).get('used_time'))
                # refresh_time = float(proxy.get(self.project_name).get('refresh_time'))
                # status = proxy.get('status', False)
                # count = int(proxy.get(self.project_name).get('count'))
                # total = int(proxy.get(self.project_name).get('total'))
                # online = proxy.get(self.project_name).get('online')

                # is_granted, ip_port, count, total = self.get_node(download_setting, proxy, node)

                # iplimit = float(download_setting.get('iplimit', 1000.0))
                # downloader_limit = float(download_setting.get('downloader_limit', 1000.0))

                project = node.get(self.project_name)
                status = node.get('status', True)
                online = project.get('online')
                used_time = float(project.get('used_time'))
                refresh_time = float(project.get('refresh_time'))
                count = int(project.get('count', 0))
                total = int(project.get('total', 0))
                now_time = float(self._get_now_timestamp())

                if status and online and used_time + iplimit <= now_time:

                    if now_time - refresh_time > 3600:
                        project.update({
                            'refresh_time': now_time,
                            'count': 0
                        })
                    if count < downloader_limit:
                        project.update({
                            'used_time': now_time,
                            'count': count + 1,
                            'total': total + 1,
                        })
                        self.r.hset(self.nodes, proxy_key, json.dumps(node))
                        self.r.save()
                        return True, proxy_key, count + 1, total + 1
                    else:
                        continue
                else:
                    continue

                # if (count == 0) or (status and online and (used_time + iplimit <= now_time)):
                #     is_granted, ip_port = True, key
                #     proxy.get(self.project_name).update({
                #         'used_time': now_time,
                #         'count': count + 1
                #     })
                #     count = count + 1
                #     self.r.hset(self.nodes, key, json.dumps(proxy))
                #     self.r.save()
                #     break
        # else:
        #     is_granted, ip_port, count, total = False, None, count, total
        
        return False, None, count, total

    def _do_alanysis_with_redis(self, node=None, download_setting=None):
        """
        :param download_setting:
        :param node:
        :return: a_json_str
        """
        is_granted = False
        ip_port = None
        count = None
        total = None

        _dict = node.get(self.project_name, {})
        if _dict:
            project = node.get(self.project_name)
            if project:
                is_granted, ip_port, count, total = self.get_node(download_setting, self.ip, node)
                print '-----' * 10, is_granted
                if not is_granted:
                    is_granted, ip_port, count, total = self.get_proxy(download_setting, node)

        else:
            self._add_node(
                node=node,
                key=self.ip,
                project_name=self.project_name,
                is_local=True
            )
            is_granted = True
            ip_port = self.ip
            count = 1
            total = 1

        return {
            'is_granted': is_granted,
            'local_ip': self.ip,
            'proxies_ip': ip_port if len(str(ip_port).split(':')) >= 2 else None,
            'count': count,
            'total': total
        }

    def _get_iplimit(self):
        """
        :return: a_dict
        """
        handler = Handler()
        projects = handler.query_projects_status_by_redis(name=self.project_name)
        if projects:
            return {
                "status": False,
                "message": "Project does not exist."
            }
        else:
            iplimit = projects[0].get("iplimit", 60)
            return {
                "status": True,
                "iplimit":iplimit,
                "downloader_limit": 60
            }

    def _get_node(self):
        """
        :return: a_dict
        """
        reference_str = self.r.hget(str(self.nodes), str(self.ip))
        print 'reference_str:', reference_str
        if reference_str is None or reference_str == 'None':
            return {}
        return json.loads(reference_str) or {}

    def get_ip(self):
        """
        Get IP Nodes Command
        :return:
        """
        download_setting = self._get_iplimit()
        print 'download_setting: ', download_setting
        if download_setting.get("status"):
            node = self._get_node()
            result = self._do_alanysis_with_redis(download_setting=download_setting, node=node)
            print result
            return result
        else:
            message = "Project does not exist."
            result = {
                'is_granted': False,
                'local_ip': self.ip,
                'proxies_ip': None,
                'message': message,
            }
            print result
            return result


class SmartProxyPool(object):

    def __init__(self):
        self.proxies = settings.PROXIES
        self.r = redis.Redis.from_url(settings.NODES_REDIS)

    def get_proxies_ip_list(self):
        try:
            resp = requests.get('http://www.proxy360.cn/default.aspx')
            if resp.status_code != 200:
                return []
            else:
                soup = BeautifulSoup(resp.content, 'html.parser')
                divs = soup.find_all('div', attrs={'class': 'proxylistitem', 'name': 'list_proxy_ip'})[:20]
                result_list = []
                for div in divs:
                    ip = div.find_all('span')[0].get_text().strip()
                    port = div.find_all('span')[1].get_text().strip()
                    ip_port = ':'.join((ip, port))
                    result_list.append(ip_port)
                print "result_list: ", result_list
                return result_list
        except Exception as e:
            print str(e)

    def _get_now_timestamp(self):
        return time.time()

    def update_redis_proxies_ip_pool(self):
        proxies_ip_list = self.get_proxies_ip_list()
        for key in self.r.hgetall(self.proxies).keys():
            if ':' in key or key=='None':
                self.r.hdel(self.proxies, key)
                self.r.save()

        for item in proxies_ip_list:
            temp_dict = {}
            temp_dict['status'] = True
            temp_dict['is_local'] = False
            temp_dict['add_time'] = self._get_now_timestamp()
            self.r.hset(self.proxies, item, json.dumps(temp_dict))
            self.r.save()

if __name__ == '__main__':
    pass