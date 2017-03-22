#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.23

import json
import time
import redis
import copy
from datetime import datetime
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
        self.ip_rule_key = settings.IP_RULE_KEY
        self.r = redis.Redis(host=settings.REDIS_IP, port=settings.REDIS_PORT, db=settings.REDIS_NUMBER)

    def _add_ip_record(self, reference_dict=None, key=None, project_name=None, is_local=False):
        # if reference_dict is not None:
        reference_dict.update({project_name: {
            "add_time": self._get_now_timestamp(),
            "last_used_time": self._get_now_timestamp(),
            "used_num": 1,
            "is_online": True
            }
        })
        if not reference_dict.has_key('status'):
            reference_dict.update({'status': True})
        if not reference_dict.has_key('is_local'):
            reference_dict.update({'is_local': is_local})
        if not reference_dict.has_key('add_time'):
            reference_dict.update({'add_time': self._get_now_timestamp()})

        self.r.hset(self.ip_rule_key, key, json.dumps(reference_dict))
        self.r.save()

    def _get_now_timestamp(self):
        return time.time()

    def _is_the_first_local_ip_can_use(self, target_dict=None, reference_dict=None):
        downloader_interval = float(target_dict.get('downloader_interval', 1000.0))
        project_in_ip = reference_dict.get(self.project_name)
        status = reference_dict.get('status', True)
        is_online = project_in_ip.get('is_online')
        last_used_time = float(project_in_ip.get('last_used_time'))
        used_num = int(project_in_ip.get('used_num', 0))
        now_time = float(self._get_now_timestamp())
        if status and is_online and last_used_time + downloader_interval <= now_time:
            project_in_ip.update({
                'last_used_time': now_time,
                'used_num': used_num + 1
            })
            used_num = used_num + 1
            # self._update_ip_record(reference_dict=reference_dict, is_local=True)
            self.r.hset(self.ip_rule_key, self.ip, json.dumps(reference_dict))
            self.r.save()
            return True, self.ip, used_num
        else:
            return False, '0.0.0.0', used_num

    def _is_the_proxies_ip_can_use(self, target_dict=None, reference_dict=None):
        downloader_interval = float(target_dict.get('downloader_interval', 1000.0))
        now_time = float(self._get_now_timestamp())
        used_num = 0
        for key in self.r.hgetall(self.ip_rule_key).keys():
            if ':' in key:
                _str = self.r.hget(self.ip_rule_key, key)
                _dict = json.loads(_str) or {}
                if (not _dict.get(self.project_name)) and _dict.get('status'):
                    self._add_ip_record(reference_dict=_dict, project_name=self.project_name, key=key, is_local=False)
                    return True, key, 1
                else:
                    last_used_time = float(_dict.get(self.project_name).get('last_used_time'))
                    status = _dict.get('status', True)
                    used_num = int(_dict.get(self.project_name).get('used_num'))
                    is_online = _dict.get(self.project_name).get('is_online')
                    if (used_num == 0) or (status and is_online and (last_used_time + downloader_interval <= now_time)):
                        is_granted, ip_port = True, key
                        _dict.get(self.project_name).update({
                            'last_used_time': now_time,
                            'used_num': used_num + 1
                        })
                        used_num = used_num + 1
                        self.r.hset(self.ip_rule_key, key, json.dumps(_dict))
                        self.r.save()
                        break
            else:
                continue
        else:
            is_granted, ip_port, used_num = False, None, used_num
        
        return is_granted, ip_port, used_num

    def _do_alanysis_with_redis(self, reference_dict=None, target_dict=None):
        """
        :param target_dict:
        :param reference_dict:
        :return: a_json_str
        """

        _dict = reference_dict.get(str(self.project_name), {})
        if _dict:
            project_in_ip = reference_dict.get(self.project_name)
            if project_in_ip:
                is_granted, ip_port, used_num = self._is_the_first_local_ip_can_use(target_dict, reference_dict)
                print '-----' * 10, is_granted
                if not is_granted:
                    is_granted, ip_port, used_num = self._is_the_proxies_ip_can_use(target_dict, reference_dict)

        else:
            self._add_ip_record(reference_dict=reference_dict, project_name=self.project_name, is_local=True)
            is_granted = True
            ip_port = self.ip
            used_num = 1

        return {
            'is_granted': is_granted,
            'local_ip': self.ip,
            'proxies_ip': ip_port if len(str(ip_port).split(':')) >= 2 else None,
            'count': used_num
        }
        
        

    def _get_target_dict(self):
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
            'name': self.project_name,
            'ip': self.ip,
            'generator_interval': one_project.generator_interval,
            'downloader_interval': one_project.downloader_interval,
            'downloader_dispatch': one_project.downloader_dispatch
        }
        return target_dict

    def _get_reference_dict(self):
        """
        :return: a_dict
        """
        reference_str = self.r.hget(str(self.ip_rule_key), str(self.ip))
        print 'reference_str:', reference_str
        if reference_str is None or reference_str == 'None':
            return {}
        return json.loads(reference_str) or {}
        

    def get_ip(self):
        target_dict = self._get_target_dict()
        reference_dict = self._get_reference_dict()
        result = self._do_alanysis_with_redis(target_dict=target_dict, reference_dict=reference_dict)
        print result
        return result


class SmartProxyPool(object):

    def __init__(self):
        self.ip_rule_key = settings.IP_RULE_KEY
        self.r = redis.Redis(host=settings.REDIS_IP, port=settings.REDIS_PORT, db=settings.REDIS_NUMBER)

    def get_proxies_ip_list(self):
        import requests
        from bs4 import BeautifulSoup
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
        for key in self.r.hgetall(self.ip_rule_key).keys():
            if ':' in key or key=='None':
                self.r.hdel(self.ip_rule_key, key)
                self.r.save()

        for item in proxies_ip_list:
            temp_dict = {}
            temp_dict['status'] = True
            temp_dict['is_local'] = False
            temp_dict['add_time'] = self._get_now_timestamp()
            self.r.hset(self.ip_rule_key, item, json.dumps(temp_dict))
            self.r.save()




if __name__ == '__main__':
    pass