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
            "last_used_time": self._get_now_timestamp(),
            "used_num": 1,
            "is_online": True
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

    def _is_local_ip_can_use(self, download_setting=None, node=None):
        """
        #
        :param download_setting:
        :param node:
        :return:
        """
        iplimit = float(download_setting.get('iplimit', 1000.0))
        project_status = node.get(self.project_name)
        status = node.get('status', True)
        is_online = project_status.get('is_online')
        last_used_time = float(project_status.get('last_used_time'))
        used_num = int(project_status.get('used_num', 0))
        now_time = float(self._get_now_timestamp())
        
        if status and is_online and last_used_time + iplimit <= now_time:
            project_status.update({
                'last_used_time': now_time,
                'used_num': used_num + 1
            })
            used_num = used_num + 1
            self.r.hset(self.nodes, self.ip, json.dumps(node))
            self.r.save()
            return True, self.ip, used_num
        else:
            return False, '0.0.0.0', used_num

    def _is_proxies_ip_can_use(self, download_setting=None, node=None):
        iplimit = float(download_setting.get('iplimit', 1000.0))
        now_time = float(self._get_now_timestamp())
        used_num = 0
        for key in self.r.hgetall(self.nodes).keys():
            if ':' in key:
                _str = self.r.hget(self.nodes, key)
                _dict = json.loads(_str) or {}
                if (not _dict.get(self.project_name)) and _dict.get('status'):
                    self._add_node(node=_dict, project_name=self.project_name, key=key, is_local=False)
                    return True, key, 1
                else:
                    last_used_time = float(_dict.get(self.project_name).get('last_used_time'))
                    status = _dict.get('status', False)
                    used_num = int(_dict.get(self.project_name).get('used_num'))
                    is_online = _dict.get(self.project_name).get('is_online')
                    if (used_num == 0) or (status and is_online and (last_used_time + iplimit <= now_time)):
                        is_granted, ip_port = True, key
                        _dict.get(self.project_name).update({
                            'last_used_time': now_time,
                            'used_num': used_num + 1
                        })
                        used_num = used_num + 1
                        self.r.hset(self.nodes, key, json.dumps(_dict))
                        self.r.save()
                        break
            else:
                continue
        else:
            is_granted, ip_port, used_num = False, None, used_num
        
        return is_granted, ip_port, used_num

    def _do_alanysis_with_redis(self, node=None, download_setting=None):
        """
        :param download_setting:
        :param node:
        :return: a_json_str
        """

        _dict = node.get(self.project_name, {})
        if _dict:
            project_status = node.get(self.project_name)
            if project_status:
                is_granted, ip_port, used_num = self._is_local_ip_can_use(download_setting, node)
                print '-----' * 10, is_granted
                if not is_granted:
                    is_granted, ip_port, used_num = self._is_proxies_ip_can_use(download_setting, node)

        else:
            self._add_node(
                node=node, key=self.ip, 
                project_name=self.project_name, is_local=True
            )
            is_granted = True
            ip_port = self.ip
            used_num = 1

        return {
            'is_granted': is_granted,
            'local_ip': self.ip,
            'proxies_ip': ip_port if len(str(ip_port).split(':')) >= 2 else None,
            'count': used_num
        }

    def _get_iplimit(self):
        """
        :return: a_dict
        """
        handler = Handler()
        projects = handler.query_projects_status_by_redis(name=self.project_name)
            
        if not projects:
            print (u'数据库查询出错了, %s project可能并不存在mongodb。' % (self.project_name))
            raise ValueError

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
        download_setting = self._get_iplimit()
        node = self._get_node()
        result = self._do_alanysis_with_redis(download_setting=download_setting, node=node)
        print result
        return result


class SmartProxyPool(object):

    def __init__(self):
        self.nodes = settings.NODES
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
        for key in self.r.hgetall(self.nodes).keys():
            if ':' in key or key=='None':
                self.r.hdel(self.nodes, key)
                self.r.save()

        for item in proxies_ip_list:
            temp_dict = {}
            temp_dict['status'] = True
            temp_dict['is_local'] = False
            temp_dict['add_time'] = self._get_now_timestamp()
            self.r.hset(self.nodes, item, json.dumps(temp_dict))
            self.r.save()

if __name__ == '__main__':
    pass