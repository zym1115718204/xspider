#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.21

import os
import re
import json
import psutil
import time
import socket
import hashlib
import datetime
import traceback
from django.conf import settings

from manager.manager import Manager
from libs.error.custom_error import IPLimitError
from collector.models import Project, Task, Result


class InitSpider(object):
    """
    Load Spider Script to Local File
    """

    def __init__(self):
        """
        LoadSpider Initialization
        """
        if not os.path.exists(settings.EXECUTE_PATH):
            os.mkdir(settings.EXECUTE_PATH)

    def load_spider(self, project):
        """
        Load Spider from  Database by project
        :param project:
        :return:
        """
        try:
            project_name = project.name
            spider_script = project.script
            models_script = project.models
            _spider_path = os.path.join(settings.EXECUTE_PATH, "%s_spider.py" %(project_name))
            _models_path = os.path.join(settings.EXECUTE_PATH, "%s_models.py" %(project_name))
            execute_init = os.path.join(settings.EXECUTE_PATH, "__init__.py")

            with open(execute_init, 'w') as fp:
                fp.write("")
            with open(_spider_path, 'w') as fp:
                fp.write(spider_script.encode('utf8'))
            with open(_models_path, 'w') as fp:
                fp.write(models_script.encode('utf8'))

        except Exception:
            print traceback.format_exc()


class Generator(object):
    """
    Generator Module
    """

    def __init__(self, project_id):
        """
        Generator Module Initialization
        :param str
        """
        self.project = Project.objects(id=project_id).first()
        InitSpider().load_spider(self.project)
        self.storage = Storage(self.project)

    def generate_task(self):
        """
        Execute Spider Generator Tasks
        :return: URL List
        :example: [{"url":"http://www.example.com","args":None}]
        """
        project_name = self.project.name

        # 调用ip管理模块
        # manager = Manager(ip='127.0.0.1', project_name=project_name)
        # ip_tactics = manager.get_ip()
        # print 'ip_tactics:', ip_tactics
        # ip_tactics_dict = json.loads(ip_tactics)
        # if ip_tactics_dict.get('granted', False) is False:
        #     return None

        _spider= __import__("execute.{0}_spider".format(project_name), fromlist=["*"])
        spider = _spider.Spider()
        result = spider.start_generator()

        return result

    def save_task(self, data):
        """
        Save Generator Result to Task Database
        :param result:
        :return:
        """
        task = []
        if not isinstance(data, list):
            raise TypeError("Generator Result Must Be List Type.")

        for url_dict in data:
            if not isinstance(url_dict, dict):
                raise TypeError("Generator URL Result Must Be Dict Type.")

            _result = self.storage.store_task(url_dict)
            task.append(_result)

        return {
            "status": True,
            "store_task": False,
            "result":task
        }

    def run_generator(self):
        """
        Run Generator
        :return:
        """
        result = self.generate_task()
        result = self.save_task(result)

        return result


class Processor(object):
    """
     Processor Module
    """
    def __init__(self, task=None, _id=None, project_id=None):
        """
        Processor Module Initialization
        :param Json
        """
        # Debug Status
        if isinstance(task, dict):
            project_id = task.get("project")
            self.project = Project.objects(id=project_id).first()
            self.storage = Storage(self.project)
            self.task = self.storage.package_task(task=task)
        # Run Status
        elif _id and project_id:
            self.project = Project.objects(id=project_id).first()
            self.storage = Storage(self.project)
            self.task = self.storage.package_task(_id=_id)
        else:
            raise TypeError("Bad Parameters.")

    def process_task(self):
        """
        Downloader Module
        :return: Result Dict
        """
        start = time.time()
        try:
            task_url = self.task.url
            args = json.loads(self.task.args)
            project_name = self.project.name

            # Manager Module
            # localhost = socket.getfqdn(socket.gethostname())
            # local_ip = socket.gethostbyname(localhost)
            _dict = psutil.net_if_addrs()
            if _dict.has_key('docker0'):
                del _dict['docker0']
            _str = str(_dict)
            m1 = re.search(r".*address='(10.\d+.\d+.\d+)'.*", _str)
            m2 = re.search(r".*address='(192.\d+.\d+.\d+)'.*", _str)
            m3 = re.search(r".*address='(172.[1-3]\d.\d+.\d+)'.*", _str)
            if m1:
                local_ip = m1.group(1)
            elif m2:
                local_ip = m2.group(2)
            elif m3:
                local_ip = m3.group(3)
            else:
                local_ip = '127.0.0.1'
            manager = Manager(ip=local_ip, project_name=project_name)
            ip_tactics = manager.get_ip()

            print ip_tactics
            ip_tactics_dict = ip_tactics
            if ip_tactics_dict.get('is_granted', False) is False:
                raise IPLimitError("IP Access is Limited, Please Wait for Access Permission.")
            else:
                if isinstance(args, basestring):
                    args = json.loads(args)
                proxies_ip = ip_tactics_dict.get('proxies_ip', {})
                if proxies_ip:
                    args.update({'proxies': {'http': 'http://%s' % (proxies_ip)}})
                args = json.dumps(args)

            _spider = __import__("execute.{0}_spider".format(project_name), fromlist=["*"])
            spider = _spider.Spider()

            resp = spider.start_downloader(task_url, args)
            result = None
            exec("result = spider.start_parser(resp, spider.{0})".format(self.task.callback))

            end = time.time()
            spend_time = end - start
            self.storage.update_task(
                task=self.task,
                status=4,
                track_log="success",
                spend_time=str(spend_time)
            )
            if self.project.status == 1:
                return {
                    "status": True,
                    "store_result": True,
                    "result": result
                }
            else:
                return {
                    "status": True,
                    "store_result": False,
                    "result": result
                }
        except IPLimitError:
            end = time.time()
            spend_time = end - start
            self.task = self.storage.update_task(
                task=self.task,
                status=0,
                track_log=traceback.format_exc(),
                spend_time=str(spend_time),
                retry_times=self.task.retry_times + 1,
            )

            return {
                "status": False,
                "store_result": False,
                "result": None,
                "reason": traceback.format_exc(),
            }

        except Exception:
            end = time.time()
            spend_time = end - start
            self.task = self.storage.update_task(
                task=self.task,
                status=3,
                track_log=traceback.format_exc(),
                spend_time=str(spend_time),
                retry_times=self.task.retry_times + 1,
            )

            return {
                "status": False,
                "store_result": False,
                "result": None,
                "reason": traceback.format_exc(),
            }

    def run_processor(self):
        """
        :return:
        """
        result = self.process_task()
        if result["status"] and result["result"].get("urls", False) is not False:
            _task = []
            for url_dict in result["result"]["urls"]:
                _result = self.storage.store_task(url_dict)
                _task.append(_result)
            result["result"] = _task

        elif result["status"]:
            result["result"] = self.storage.store_result(result["result"])

        return result


class Storage(object):
    """
    Storage Module
    """

    def __init__(self, project):
        """
        Initialization
        """
        self.project = project

    def store_task(self, url_dict):
        """
        Store Generator Task
        :return:
        :Porject Debug,  Task Dict
        :Porject    ON,  Store Status Dict
        """
        try:
            _status = self.project.status
            if _status == 1:

                # Save Task to Database
                url = url_dict.get("url")
                args = url_dict.get("args")
                callback = url_dict.get("callback")
                task_id = self.str2md5(url_dict.get("url"))

                repeat = None
                task_object = None
                exec ("from execute.{0}_models import *".format(self.project.name))
                exec("repeat = {0}{1}.objects(task_id=task_id).first()".format(str(self.project.name).capitalize(), "Task"))

                if repeat:
                    return{
                        "status": True,
                        "store_task": False,
                        "repeat": True,
                    }
                else:
                    exec ("task_object = {0}{1}()".format(str(self.project.name).capitalize(), "Task"))
                    task_object.project = self.project
                    task_object.args = json.dumps(args)
                    task_object.callback = callback
                    task_object.task_id = task_id
                    task_object.status = 0
                    task_object.url = url

                    task_object.save()

                    return {
                        "status": True,
                        "store_task": True
                    }

            elif _status == 2:
                task_object = {}

                # Create Debug Task Object && Dynamic Import Models
                url = url_dict.get("url")
                print url
                args = url_dict.get("args")
                callback = url_dict.get("callback")
                task_id = self.str2md5(url_dict.get("url"))

                task_object["project"] = str(self.project.id)
                task_object["args"] = json.dumps(args)
                task_object["callback"] = callback
                task_object["task_id"] = task_id
                task_object["status"] = 0
                task_object["url"] = url

                return {
                    "status": True,
                    "store_task": False,
                    "result": task_object
                }
            else:
                raise TypeError("Project Status Must Be On or Debug.")

        except UnicodeEncodeError:
            return{
                "status": False,
                "store_task": False,
                "result": url_dict
            }

    def package_task(self, task=None, _id=None):
        """
        Package Task
        :return:
        """
        _name = self.project.name
        _status = self.project.status

        if _status == 1:
            exec ("from execute.{0}_models import *".format(_name))
            exec ('self.task = {0}Task.objects(id="{1}").first()'.format(str(_name).capitalize(), _id))
            return self.task

        elif _status == 2:
            task_object = None
            exec ("from execute.{0}_models import *".format(_name))
            exec ("task_object = {0}{1}()".format(str(_name).capitalize(), "Task"))

            args = task.get("args")
            url = task.get("url")
            callback = task.get("callback")
            task_id = self.str2md5(task.get("url"))

            task_object.project = self.project
            task_object.task_id = task_id
            task_object.callback = callback
            task_object.args = json.dumps(args)
            task_object.status = 0
            task_object.url = url
            self.task = task_object

            return self.task
        else:
            raise TypeError("Project Status Must Be Run or Debug.")

    def update_task(self, task, status, track_log, spend_time, retry_times=0):
        """
        Update Task
        :return:
        """
        _status = self.project.status
        if _status == 1:
            task.update(
                status=status,
                track_log=track_log,
                update_datetime=datetime.datetime.now(),
                spend_time=spend_time,
                retry_times=retry_times,
            )
            return task

        elif _status== 2:
            task.status = status,
            task.track_log = track_log,
            task.update_datetime = datetime.datetime.now(),
            task.spend_time = spend_time,
            task.retry_times = retry_times

            return task
        else:
            raise TypeError("Project Status Must Be Run or Debug.")

    def store_result(self, result):
        """
        Store Result
        :return:
        """
        _status = self.project.status
        if _status == 1:
            # Save Task Result to Database
            task_result = None
            exec ("from execute.{0}_models import *".format(self.project.name))
            exec ("task_result = {0}{1}()".format(str(self.project.name).capitalize(), "Result"))

            task_result.project = self.project
            task_result.task = self.task
            task_result.url = self.task.url
            task_result.update_datetime = datetime.datetime.now()
            task_result.result = json.dumps(result)
            task_result.save()

            return {
                "store_result": True
            }

        elif _status == 2:

            # Save Task Result to Object
            # exec ("from execute.{0}_models import *".format(self.project.name))
            # exec ("task_result = {0}{1}()".format(str(self.project.name).capitalize(), "Result"))
            # task_result.project = self.project
            # task_result.task = self.task
            # task_result.url = self.task.url
            # task_result.update_datetime = datetime.datetime.now()
            # task_result.result = result

            task_result = {}
            task_result["project"] = str(self.project.id)
            task_result["url"] = self.task.url
            task_result["update_datetime"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            task_result["result"] = result

            return task_result
        else:
            raise TypeError("Project Status Must Be On or Debug.")

    @staticmethod
    def str2md5(string):
        """
        Convert Str to MD5
        :return:
        """
        md5 = hashlib.md5()
        md5.update(string.encode('utf8'))

        return md5.hexdigest()
