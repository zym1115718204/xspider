#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created on 2017-03-2
# Project: Web Handler

import os
import json
import redis
import string
import datetime
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
    Xspider Handler Route Module
    """
    def __init__(self):
        """
        Parameters Initialization
        """
        self._query = Query()
        self._command = Command()

    def query_all_projects_status(self, request, name="--all"):
        """
        Query Projects Status to Redis
        """
        _projects = self._query.query_projects_by_name(name)
        projects = []
        for project in _projects:
            name = project.name
            group = project.group
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
                'group': group,
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
            'job_name1':{'id':id,},
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
                'group': project.group,
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

    def edit_project_settings(self, data):
        """
        Edit Project Settings Route
        :param data:
        :return:
        """
        result = self._command.edit_project_settings(data)
        return result

    def create_project(self, project, host="http://www.example.com"):
        """
        Create Project Route
        :param project:
        :param host:
        :return:
        """
        result = self._command.create_project(project, host)
        return result


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
        Get Projects by Name
        :return: jobs list
        """
        name = smart_unicode(name)
        if not name:
            return
        if name == "--all":
            projects = Project.objects()
        else:
            projects = Project.objects(name=name)

        return projects


class Command(object):
    """
    Command Handler
    """

    def __init__(self):
        """
        Initialization
        """
        pass

    def edit_project_settings(self, data):
        """
        Edit Project Settings
        :return:
        """

        name = data.get("project")
        project = Project.objects(name=name).first()
        if project is None:
            return {
                "status": False,
                "project": name,
                "message": "Bab Parameters",
                "code": 4002,
            }
        else:
            try:
                if data.get("group", False):
                    project.update(group=str(data.get("group")))
                if data.get("timeout", False):
                    project.update(timeout=int(data.get("timeout")))
                if data.get("status", False):
                    project.update(status=int(data.get("status")))
                if data.get("priority", False):
                    project.update(priority=int(data.get("priority")))
                if data.get("info", False):
                    project.update(info=str(data.get("info")))
                if data.get("script", False):
                    project.update(script=str(data.get("script")))
                if data.get("interval", False):
                    project.update(generator_interval=str(int(data.get("interval"))))
                if data.get("ip_limit", False):
                    project.update(downloader_interval=str(int(data.get("ip_limit"))))
                if data.get("number", False):
                    project.update(downloader_dispatch=int(data.get("number")))

                project.update(update_datetime=datetime.datetime.now())

            except ValueError:
                return {
                    "status": False,
                    "project": name,
                    "message": "Bad Parameters",
                    "code": 4003,
                }
            except Exception:
                return {
                    "status": False,
                    "project": name,
                    "message": "Internal Server Error",
                    "code": 5001
                }

        return {
            "status": True,
            "project": name,
            "message": "Operation Succeeded",
            "code": 2001
        }

    def create_project(self, project_name, host="http://www.example.com"):
        """
        Create Project
        :return:
        """
        project_name = project_name.strip()
        result = self.start_project(project_name, host)
        if result["status"] is True:
            result = self.load_project(project_name)
            return result
        else:
            return result

    @staticmethod
    def start_project(project_name, host="http://www.example.com"):
        """
        Start Project
        :return:
        """
        try:
            _projectname = project_name.lower()
            project_path = os.path.join(settings.PROJECTS_PTAH, _projectname)
            if not os.path.exists(project_path):
                os.makedirs(project_path)

            tmpl_path = os.path.join(settings.BASE_DIR, 'libs', 'template', 'spider.tmpl')
            with open(tmpl_path, 'rb') as fp:
                raw = fp.read().decode('utf8')
            create_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            content = string.Template(raw).substitute(CREATE_TIME=create_time,
                                                      PROJECTS_NAME=_projectname,
                                                      START_URL=host)

            spider_path = os.path.join(project_path, '%s_spider.py' % (_projectname))
            if not os.path.exists(spider_path):
                with open(spider_path, 'w') as fp:
                    fp.write(content.encode('utf8'))
                msg = 'Successfully create a new project %s !' % (_projectname)
                print msg
            else:
                msg = 'Failed to create project %s , Project already exists! ' % (_projectname)
                return {
                    "status": False,
                    "reason": msg,
                    "msg": msg
                }

            tmpl_path = os.path.join(settings.BASE_DIR, 'libs', 'template', 'models.tmpl')
            with open(tmpl_path, 'rb') as fp:
                raw = fp.read().decode('utf8')
            create_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            content = string.Template(raw).substitute(CREATE_TIME=create_time,
                                                      PROJECTS_NAME=_projectname,
                                                      PROJECTS_NAME_TASK=str(_projectname).capitalize() + 'Task',
                                                      PROJECTS_NAME_RESULT=str(
                                                          _projectname).capitalize() + 'Result')

            models_path = os.path.join(project_path, '%s_models.py' % (_projectname))
            if not os.path.exists(models_path):
                with open(models_path, 'w') as fp:
                    fp.write(content.encode('utf8'))
                msg = 'Successfully create a new project models %s !' % (models_path)
                return {
                    "status": True,
                    "reason": msg,
                    "msg": msg
                }
            else:
                msg = 'Failed to create project %s , Project already exists! ' % (models_path)
                return {
                    "status": False,
                    "reason": msg,
                    "msg": msg
                }

        except Exception:
            reason = traceback.format_exc()
            msg = 'Failed to create new project %s !, reason: %s' % (project_name, reason)
            return {
                "status": False,
                "reason": reason,
                "msg": msg
            }

    def load_project(self, project_name):
        """
        Load Project
        :return:
        """
        try:
            project_path = os.path.join(settings.PROJECTS_PTAH, project_name)
            if not os.path.exists(project_path):
                os.makedirs(project_path)

            spider_path = os.path.join(project_path, '%s_spider.py' % (project_name))
            models_path = os.path.join(project_path, '%s_models.py' % (project_name))
            if not os.path.exists(spider_path) or not os.path.exists(models_path):
                msg = 'Failed to load project %s , Project does not exist! ' % (project_name)
                return {
                    "status": False,
                    "reason": msg,
                    "msg": msg
                }
            else:
                result = self._load_project(project_name, spider_path, models_path)
                return result

        except Exception:
            reason = traceback.format_exc()
            msg = ('Failed to create new project %s !, Reason: %s' % (project_name, reason))

            return {
                "status": False,
                "reason": reason,
                "msg": msg
            }

    def _load_project(self, project_name, spider_path, models_path):
        """
        _load project
        :param project_name:
        :param spider_path:
        :param models_path:
        :return:
        """
        try:
            with open(spider_path, 'rb') as fp:
                spider_script = fp.read().decode('utf8')
            with open(models_path, 'rb') as fp:
                models_script = fp.read().decode('utf8')
            project = Project.objects(name=project_name).first()
            if project:
                project.update(script=spider_script)
                project.update(models=models_script)
            else:
                project = Project(name=project_name,
                                  info="",
                                  script=spider_script,
                                  models=models_script,
                                  generator_interval="60",
                                  downloader_interval="60",
                                  downloader_dispatch=1)
                project.save()
            msg = 'Successfully load project %s !' % (project_name)
            return {
                "status": True,
                "reason": msg,
                "msg": msg
            }

        except Exception:
            reason = traceback.format_exc()
            msg = 'Failed to load project %s !, Reason: %s' % (spider_path, reason)
            return {
                "status": False,
                "reason": msg,
                "msg": msg
            }