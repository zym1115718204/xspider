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

    def __init__(self):
        """
        Generator Module Initialization
        """
        pass


class Processor(object):
    """
     Processor Module
    """