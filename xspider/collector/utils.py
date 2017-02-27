#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.21

import os
import json
import hashlib
import socket
import traceback
from django.conf import settings

# Database Models
from collector.models import Project, Task, Result

# Manager
from manager.manager import Manager


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

    def generate_task(self):
        """
        Execute Spider Generator Tasks
        :return: URL List
        :example: [{"url":"http://www.example.com","args":None}]
        """
        project_name = self.project.name

        # 调用ip管理模块
        # manager = Manager(ip='localhost', project_name=project_name)
        # ip_tactics = manager.get_ip()
        # print ip_tactics
        # ip_tactics_dict = json.loads(ip_tactics)
        # if ip_tactics_dict.get('granted', False) is False:
        #     return None

        _generator = __import__("execute.{0}_spider".format(project_name), fromlist=["*"])
        spider_generator = _generator.Generator()
        result = spider_generator.start_generator()

        return result

    def save_task(self, result):
        """
        Save Generator Result to Task Database
        :param result:
        :return:
        """
        if not isinstance(result, list):
            raise TypeError("Generator Result Must Be List Type.")

        for url_dict in result:
            if not isinstance(url_dict, dict):
                raise TypeError(("Generator URL Result Must Be Dict Type."))

            if self.project.status == 1:
                # Save Task to Database
                exec ("from execute.{0}_models import *".format(self.project.name))
                exec ("task_object = {0}{1}()".format(str(self.project.name).capitalize(), "Task"))

                url = url_dict.get("url")
                args = url_dict.get("args")
                task_id = self.str2md5(url_dict.get("url"))

                task_object.project = self.project
                task_object.task_id = task_id
                task_object.status = 0
                task_object.url = url
                task_object.args = json.dumps(args)
                task_object.save()



            elif self.project.status == 2:
                task_object = {}
                # Create Debug Task Object && Dynamic Import Models
                url = url_dict.get("url")
                task_id = self.str2md5(url_dict.get("url"))

                task_object["project"] = str(self.project.id)
                task_object["task_id"] = task_id
                task_object["status"] = 0
                task_object["url"] = url
                task_object["args"] = {}

                return task_object
            else:
                return url_dict

    @staticmethod
    def str2md5(string):
        """
        Convert Str to MD5
        :return:
        """
        md5 = hashlib.md5()
        md5.update(string)

        return md5.hexdigest()

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
        if isinstance(task, dict):
            project_id = task.get("project")
            self.project = Project.objects(id=project_id).first()
        elif _id and project_id:
            self.project = Project.objects(id=project_id).first()
        else:
            raise TypeError("Bad Parameters.")

        _name = self.project.name
        _status = self.project.status

        if _status == 1:
            exec ("from execute.{0}_models import *".format(_name))
            exec('self.task = {0}Task.objects(id="{1}").first()'.format(str(_name).capitalize(), _id))
        elif _status == 2:
            exec ("from execute.{0}_models import *".format(_name))
            exec ("task_object = {0}{1}()".format(str(_name).capitalize(), "Task"))

            args = task.get("args")
            url = task.get("url")
            task_id = self.str2md5(task.get("url"))

            task_object.project = self.project
            task_object.task_id = task_id
            task_object.args = json.dumps(args)
            task_object.status = 0
            task_object.url = url
            self.task = task_object
        else:
            raise TypeError("Project Status Must Be On or Debug.")

    def process_task(self):
        """
        Downloader Module
        :return: Result Dict
        """
        try:
            task_url = self.task.url
            args = json.loads(self.task.args)

            project_name = self.project.name

            # # 调用ip管理模块
            # # 获取本机电脑名
            # myname = socket.getfqdn(socket.gethostname())
            # # 获取本机ip
            # local_ip = socket.gethostbyname(myname)
            # manager = Manager(ip=local_ip, project_name=project_name)
            # ip_tactics = manager.get_ip()
            # print ip_tactics
            # ip_tactics_dict = json.loads(ip_tactics)
            # if ip_tactics_dict.get('is_granted', False) is False:
            #     return None
            # else:
            #     args = json.loads(args)
            #     proxies_ip = ip_tactics_dict.get('proxies_ip', {})
            #     if proxies_ip:
            #         args.update({'proxies': {'http': 'http://%s' % (proxies_ip)}})
            #     args = json.dumps(args)

            _spider = __import__("execute.{0}_spider".format(project_name), fromlist=["*"])
            _downloader = _spider.Downloader()
            _parser = _spider.Parser()

            resp = _downloader.start_downloader(task_url, args)
            result = _parser.start_parser(resp)

            self.task.update(status=4)

            return result

        except Exception:
            self.task.update(status=4)
            return traceback.format_exc()
            # record log

    def save_result(self, result):
        """

        :return:
        """
        # if not isinstance(result, dict):
        #     raise TypeError(("Processor Result Must Be Dict Type."))
        if self.project.status == 1:
            # Save Task to Database
            # TODO
            pass
        elif self.project.status == 2:
            print result
        else:
            print result

    def run_processor(self):
        """
        :return:
        """
        result = self.process_task()
        self.save_result(result)
        return result

    @staticmethod
    def str2md5(string):
        """
        Convert Str to MD5
        :return:
        """
        md5 = hashlib.md5()
        md5.update(string)

        return md5.hexdigest()

