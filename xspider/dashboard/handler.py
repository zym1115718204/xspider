#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 2017-03-2
# Project: Web Handler

import os
import json
import redis
import traceback

from django.conf import settings
from django.utils.encoding import smart_unicode

from collector.models import Project


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


class Handler(object):
    """
    Xspider Handler Module
    """

    def __init__(self):
        """
        Parameters Initialization
        """
        self._query = Query()

    def query_all_projects_status(self, request, name="--all"):
        """
        Query Projects Status to Redis
        """
        _projects = self._query.query_projects_by_name(name)
        projects = []
        for project in _projects:
            name = project.name
            model = "{0}Task".format(str(name).capitalize())
            # Notice: Checking
            exec ("from execute.{0}_models import *".format(name))
            exec("total = {0}.objects().count()".format(model))
            exec("new = {0}.objects(status={0}.STATUS_LIVE).count()".format(model))
            exec("success = {0}.objects(status={0}.STATUS_SUCCESS).count()".format(model))
            exec("failed = {0}.objects(status={0}.STATUS_FAIL).count()".format(model))
            exec("invalid = {0}.objects(status={0}.STATUS_INVALID).count()".format(model))

            iplimit = project.downloader_interval
            priority = project.priority
            script = project.script
            models = project.models
            interval = project.generator_interval
            speed = project.downloader_dispatch
            status = project.status
            timeout = project.timeout

            job_dict = {
                'id': str(project.id),
                'name': name,
                'info': project.info,
                'status': status,
                'priority': priority,
                'script': script,
                'models': models,
                'interval': interval,
                'total': total,
                'new': new,
                'success': success,
                'failed': failed,
                'invalid': invalid,
                'iplimit': iplimit,
                'speed': speed,
                'timeout': timeout,
                'update_datetime': project.update_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                'add_datetime': project.add_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            }

            projects.append(job_dict)

        # Store Redis
        r = redis.Redis.from_url(settings.ANALYSIS_REDIS)
        for data in projects:
            REDIS_TABLE = "{0}_status".format(data.get("name"))
            r.hset(REDIS_TABLE, data.get("name"), json.dumps(data))

        return projects

    def query_projects_status_by_redis(self, request, name="--all"):
        """
        Query Projects Status from Redis
         :return:
         data:
        {
            'job_name1':{
                        'id':id,
                    },
            'job_name2':{},
        }
        """
        r = redis.Redis.from_url(settings.ANALYSIS_REDIS)
        _projects = self._query.query_projects_by_name(name)
        projects = []
        for project in _projects:
            REDIS_TABLE = "{0}_status".format(project.name)
            r_dict = r.hgetall(REDIS_TABLE)

            if r_dict:
                project_status = json.loads(r_dict[project.name])
                total = int(project_status.get('total', "N/A"))
                new = int(project_status.get('new', "N/A"))
                success = int(project_status.get('success', "N/A"))
                failed = int(project_status.get('failed', "N/A"))
                invalid = int(project_status.get('invalid', "N/A"))
            else:
                total = 0
                new = 0
                success = 0
                failed = 0
                invalid = 0

            job_dict = {
                'id': str(project.id),
                'name': project.name,
                'info': project.info,
                'status': project.status,
                'priority': project.priority,
                'script': project.script,
                'models': project.models,
                'interval': int(project.generator_interval),
                'total': total,
                'new': new,
                'success': success,
                'failed': failed,
                'invalid': invalid,
                'speed': int(project.downloader_dispatch),
                'iplimit': int(project.downloader_interval),
                'timeout': int(project.timeout),
                'update_datetime': project.update_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                'add_datetime': project.add_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            }

            projects.append(job_dict)

        return projects

class Query(object):
    """
    Query Handler
    """

    def __init__(self):
        """
        Initialization
        """
        pass

    @staticmethod
    def query_projects_by_name(name):
        """
        Get jobs by exact query
        :return: jobs list
        """
        # 参数检查并转字符串
        name = smart_unicode(name)
        if not name:
            return
        if name == "--all":
            projects = Project.objects()
        else:
            projects = Project.objects(name=name)
        return projects