#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.21

import os
import json
import hashlib
import traceback
from django.conf import settings

# Database Models
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

    def generate_task(self):
        """
        Execute Spider Generator Tasks
        :return: URL List
        :example: [{"url":"http://www.example.com","args":None}]
        """
        project_name = self.project.name
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
                task_object.args = args
                task_object.save()

                # TODO

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

                return json.dumps(task_object)
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
    def __init__(self, task):
        """
        Processor Module Initialization
        :param Json
        """
        task = json.loads(task)
        project_id = task.get("project")
        _task_id = task.get("id")
        self.project = Project.objects(id=project_id).first()

        if self.project.status == 1:
            exec ("from execute.{0}_models import *".format(self.project.name))
            # self.task = BaiduTask.objects(id=_task_id).first()
            exec("self.task = {0}_Task.objects(id={1}).first()".format(str(self.project.name).capitalize(),_task_id))
        elif self.project.status == 2:
            exec ("from execute.{0}_models import *".format(self.project.name))
            exec ("task_object = {0}{1}()".format(str(self.project.name).capitalize(), "Task"))

            args = task.get("args")
            url = task.get("url")
            task_id = self.str2md5(task.get("url"))

            task_object.project = self.project
            task_object.task_id = task_id
            task_object.args = args
            task_object.status = 0
            task_object.url = url
            self.task = task_object
        else:
            raise TypeError("Project Status Must Be Running or Debug.")

    def process_task(self):
        """
        Downloader Module
        :return: Result Dict
        """
        try:
            task_url = self.task.url
            args = self.task.args

            project_name = self.project.name
            _spider = __import__("execute.{0}_spider".format(project_name), fromlist=["*"])
            _downloader = _spider.Downloader()
            _parser = _spider.Parser()

            resp = _downloader.start_downloader(task_url, args)
            result = _parser.start_parser(resp)

            return result
            # record log

        except Exception:

            print traceback.format_exc()
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


