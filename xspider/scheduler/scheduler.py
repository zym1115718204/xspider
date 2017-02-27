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
    def _filter_projects():
        """
        Projects Filter
        :return:
        """
        _projects = Project.objects(status=Project.STATUS_DEBUG).order_by('+priority')
        projects = []
        for project in _projects:
            now = datetime.datetime.now()
            last = project.last_generator_time
            interval = int(project.generator_interval)
            if not project.last_generator_time:
                project.update(last_generator_time=now)
                continue
            next = last + datetime.timedelta(seconds=interval)
            if next <= now:
                projects.append(project)
                project.update(last_generator_time=now)
            else:
                continue

        return projects

    def generator_dispatch(self):
        """
        Generator Dispatch
        :return:
        """
        projects = self._filter_projects()
        print projects
        for project in projects:
            print project.name
            print project.priority
            _priority = project.priority
            if _priority == -1:
                celery.high_generator.delay(str(project.id))
            elif _priority <= 3:
                celery.mid_generator.delay(str(project.id))
            else:
                celery.low_generator.delay(str(project.id))

        return {
            'status': True,
            "projects": len(projects)
        }

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
        _priority = project.priority_pro
        if _priority == -1:
            for task in tasks:
                celery.high_processor.delay(str(task.id))
        elif _priority <= 3:
            for task in tasks:
                celery.mid_processor.delay(str(task.id))
        else:
            for task in tasks:
                celery.low_processor.delay(str(task.id))

        return {
            "project": str(project.name),
            "tasks": len(tasks)
         }

    def processor_dispatch(self):
        """
        Processor Dispatch
        :return:
        """
        results = []
        projects = self._filter_projects()
        print projects
        for project in projects:
            tasks = self._filter_tasks(project)
            result = self._processor_tasks(project, tasks)
            results.append(result)

        return results

    @staticmethod
    def run_threaded(job_func):
        job_thread = threading.Thread(target=job_func)
        job_thread.start()
        # print threading.enumerate()

    def run(self):
        schedule.every(10).seconds.do(self.run_threaded, self.generator_dispatch)
        # schedule.every(self.generator_dispatch_interval).seconds.do(self.run_threaded, self.generator_dispatch)
        # schedule.every(self.downloader_dispatch_interval).seconds.do(self.run_threaded, self.downloader_dispatch)
        # schedule.every(self.structure_dispatch_interval).seconds.do(self.run_threaded, self.parser_dispatch)
        # schedule.every(self.extracter_dispatch_interval).seconds.do(self.run_threaded, self.extracter_dispatch)

        while True:
            schedule.run_pending()
            time.sleep(1)