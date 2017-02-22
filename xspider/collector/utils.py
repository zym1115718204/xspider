#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.21

import os
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
            project = Project.objects().first()
            project_name = project.name
            spider_script = project.script
            execute_path = os.path.join(settings.EXECUTE_PATH, "%s_spider.py" %(project_name))
            execute_init = os.path.join(settings.EXECUTE_PATH, "__init__.py")

            with open(execute_init, 'w') as fp:
                fp.write("")
            with open(execute_path, 'w') as fp:
                fp.write(spider_script.encode('utf8'))

        except Exception:
            print traceback.format_exc()


class Generator(object):
    """
    Generator Module
    """

    def __init__(self, project):
        """
        Generator Module Initialization
        """

        self.project = project
        InitSpider().load_spider(self.project)

    def execute_task(self):
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
        if not isinstance(result,list):
            raise TypeError("Generator Result Must Be List Type.")
        for i in result:
            if not isinstance(i,dict):
                raise TypeError(("Generator URL result Must Be Dict Type."))
            print i

    def run_generator(self):
        """
        Run Generator
        :return:
        """
        result = self.execute_task()
        self.save_task(result)


class Processor(object):
    """
     Processor Module
    """
    pass
