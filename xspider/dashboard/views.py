#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from dashboard.handler import Handler

import os


# Create your views here.

def test_current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body><h2>Welcome to Xspider！ It's Worked! </h2>It is now %s.</body></html>" % (now,)
    return HttpResponse(html)


def index(request):
    """
    Dashboard Index Page
    :param request:
    :return:
    """
    handler = Handler()
    projects = handler.query_projects_status_by_redis(request)

    for project in projects:
        if project['total'] >= 0 and project['total'] != project['new']:
            _task_num = float(project['total'] - project['new'])
            project['success_rate'] = round(100 * project['success'] / _task_num, 2)
            project['failed_rate'] = round(100 * project['failed'] / _task_num, 2)
            project['invalid_rate'] = round(100 * project['invalid'] / _task_num, 2)
            project['schedule'] = round((_task_num / project['total']) * 100, 2)
        else:
            project['succ_rate'] = 0
            project['failed_rate'] = 0
            project['invalid_rate'] = 0
            project['schedule'] = 0

    return render_to_response("index.html", {'projects': projects, 'tasks': None, 'profile': None})


def test(request):
    """
    Dashboard Index Page
    :param request:
    :return:
    """
    return render_to_response("dashboard.html", {'jobs': None, 'tasks': None, 'profile': None})