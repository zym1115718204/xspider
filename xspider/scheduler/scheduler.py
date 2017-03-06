#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.24


import time
import datetime
import schedule
import threading

from xspider import celery
from collector.models import Project

from django.conf import settings


class XspiderScheduler(object):
    """
    Xspider Modelule
    """
    def __init__(self):
        """
        Models Initialization
        """
        # Project.object(status=STATUS_ON).order_by('+priority')
        pass

    @staticmethod
    def _filter_generator_projects():
        """
        Projects Filter
        :return:
        """
        _projects = Project.objects(status=Project.STATUS_ON).order_by('+priority')
        projects = []
        for project in _projects:
            now = datetime.datetime.now()
            last = project.last_generator_time
            interval = int(project.generator_interval)
            if not project.last_generator_time:
                projects.append(project)
                project.update(last_generator_time=now)
                continue
            next = last + datetime.timedelta(seconds=interval)
            if next <= now:
                projects.append(project)
                project.update(last_generator_time=now)
            else:
                continue

        return projects

    @staticmethod
    def _filter_processor_projects():
        """
        Projects Filter
        :return:
        """
        _projects = Project.objects(status=Project.STATUS_ON).order_by('+priority')
        projects = []
        for project in _projects:
            projects.append(project)

        return projects

    def run_generator_dispatch(self):
        """
        Generator Dispatch
        :return:
        """
        projects = self._filter_generator_projects()
        for project in projects:
            _priority = project.priority
            if _priority == -1:
                celery.high_generator.delay(str(project.id))
            elif _priority <= 3:
                celery.mid_generator.delay(str(project.id))
            else:
                celery.low_generator.delay(str(project.id))

        result = {
            'status': True,
            "projects": len(projects)
        }

        print "[{0}]::Generator Dispatch::{1}".format(datetime.datetime.now(), result)
        return result

    @staticmethod
    def _filter_tasks(project):
        """
        Filter Tasks by Project
        :return:
        """
        _name = project.name

        _num = project.downloader_dispatch
        exec("from execute.{0}_models import {1}Task".format(_name, str(_name).capitalize()))
        exec("tasks = {0}Task.objects(status=0)[0:{1}]".format(str(_name).capitalize(), int(_num)))

        return tasks

    @staticmethod
    def _processor_tasks(project, tasks):
        """
        Dispatch Tasks by Project
        :return:
        """
        _priority = project.priority
        if _priority == -1:
            for task in tasks:
                celery.high_processor.delay(str(task.id), str(project.id))
                task.update(status=1)
        elif _priority <= 3:
            for task in tasks:
                celery.mid_processor.delay(str(task.id), str(project.id))
                task.update(status=1)
        else:
            for task in tasks:
                celery.low_processor.delay(str(task.id), str(project.id))
                task.update(status=1)

        return {
            "project": str(project.name),
            "tasks": len(tasks)
         }

    def run_processor_dispatch(self):
        """
        Processor Dispatch
        :return:
        """
        results = []
        projects = self._filter_processor_projects()

        for project in projects:
            tasks = self._filter_tasks(project)
            result = self._processor_tasks(project, tasks)
            results.append(result)

        print "[{0}]::Processor Dispatch::{1}".format(datetime.datetime.now(),results)
        return results

    @staticmethod
    def run_threaded(job_func):
        job_thread = threading.Thread(target=job_func)
        job_thread.start()
        # print threading.enumerate()

    def run(self):
        schedule.every(1).seconds.do(self.run_threaded, self.run_generator_dispatch)
        schedule.every(1).seconds.do(self.run_threaded, self.run_processor_dispatch)

        while True:
            schedule.run_pending()
            time.sleep(1)