#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from dashboard.handler import Handler
from libs.decorator.decorator import render_json

from django.views.decorators.csrf import csrf_exempt



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

        if project['total_d'] >= 0 and project['total_d'] != project['new_d']:
            _task_num = float(project['total_d'] - project['new_d'])
            project['success_rate_d'] = round(100 * project['success_d'] / _task_num, 2)
            project['failed_rate_d'] = round(100 * project['failed_d'] / _task_num, 2)
            project['invalid_rate_d'] = round(100 * project['invalid_d'] / _task_num, 2)
            project['schedule_d'] = round((_task_num / project['total_d']) * 100, 2)
        else:
            project['succ_rate_d'] = 0
            project['failed_rate_d'] = 0
            project['invalid_rate_d'] = 0
            project['schedule_d'] = 0

        if project['total_h'] >= 0 and project['total_h'] != project['new_h']:
            _task_num = float(project['total_h'] - project['new_h'])
            project['success_rate_h'] = round(100 * project['success_h'] / _task_num, 2)
            project['failed_rate_h'] = round(100 * project['failed_h'] / _task_num, 2)
            project['invalid_rate_h'] = round(100 * project['invalid_h'] / _task_num, 2)
            project['schedule_h'] = round((_task_num / project['total_h']) * 100, 2)
        else:
            project['succ_rate_h'] = 0
            project['failed_rate_h'] = 0
            project['invalid_rate_h'] = 0
            project['schedule_h'] = 0

        if project['total_m'] >= 0 and project['total_m'] != project['new_m']:
            _task_num = float(project['total_m'] - project['new_m'])
            project['success_rate_m'] = round(100 * project['success_m'] / _task_num, 2)
            project['failed_rate_m'] = round(100 * project['failed_m'] / _task_num, 2)
            project['invalid_rate_m'] = round(100 * project['invalid_m'] / _task_num, 2)
            project['schedule_m'] = round((_task_num / project['total_m']) * 100, 2)
        else:
            project['succ_rate_m'] = 0
            project['failed_rate_m'] = 0
            project['invalid_rate_m'] = 0
            project['schedule_m'] = 0

    return render_to_response("index.html", {'projects': projects, 'tasks': None, 'profile': None,})


@csrf_exempt
@render_json
def debug(request, name):
    """
    Debug index page
    :param request:
    :return:
    """
    handler = Handler()
    projects = handler.query_projects_status_by_redis(request, name=name)
    project = projects[0]

    return render_to_response("debug.html", {'project': project})


@csrf_exempt
@render_json
def data(request):
    """
    Data index page
    :param request:
    :return:
    """
    handler = Handler()
    projects = handler.query_projects_status_by_redis(request)

    return render_to_response("data.html", {"projects": projects})


@csrf_exempt
@render_json
def result(request, name):
    """
    Result detail index page
    :param request:
    :return:
    """
    if name is not None:
        handler = Handler()
        projects = handler.query_projects_status_by_redis(request, name=name)

        return render_to_response("result.html", {"project": projects[0]})
    else:
        return
        # todo


@csrf_exempt
@render_json
def task(request):
    """
    Task index page
    :param request:
    :return:
    """
    handler = Handler()
    projects = handler.query_projects_status_by_redis(request)

    return render_to_response("task.html", {"projects": projects})


@csrf_exempt
@render_json
def log(request, task_id):
    """
    Task index page
    :param request:
    :return:
    """
    handler = Handler()
    projects = handler.query_projects_status_by_redis(request)

    return render_to_response("log.html", {"projects": projects})


@csrf_exempt
@render_json
def api(request):
    """
    API index page
    :param request:
    :return:
    """
    return render_to_response("api.html")


@csrf_exempt
@render_json
def edit_project(request):
    """
    Edit Project Command API
    :param request:
    :return:
    """
    data = request.POST
    command = data.get("command")
    group = data.get("group")
    name = data.get("project")
    timeout = data.get("timeout")
    status = data.get("status")
    priority = data.get("priority")
    info = data.get("info")
    script = data.get("script")
    interval = data.get("interval")
    number = data.get("number")
    ip_limit = data.get("ip_limit")

    if command and name and (
        group or timeout or status or priority or info or script or interval or number or ip_limit):
        handler = Handler()
        result = handler.edit_project_settings(data)
    else:
        result = {
            "status": False,
            "project": name,
            "message": "Bad Parameters",
            "code": 4001,
        }

    return result


@csrf_exempt
@render_json
def create_project(request):
    """
    Create Project Command API
    :param request:
    :return:
    """
    name = request.POST.get("project")
    command = request.POST.get("command")
    url = request.POST.get("url")

    if name and command:
        handler = Handler()
        if url is not None:
            url = url.strip()
            result = handler.create_project(name, url)
        else:
            result = handler.create_project(name)
    else:
        result = {
            "status": False,
            "project": name,
            "message": "Bad Parameters",
            "code": 4001,
        }
    return result


@csrf_exempt
@render_json
def run_project(request):
    """
    Run Projcet Generator Command API
    :param request:
    :return:
    """
    name = request.POST.get("project")
    command = request.POST.get("command")
    task = request.POST.get("task")

    if name and command and task:
        handler = Handler()
        result = handler.run_processor(name, json.loads(task))
    elif name and command:
        handler = Handler()
        result = handler.run_generator(name)
    else:
        result = {
            "status": False,
            "project": name,
            "message": "Bad Parameters",
            "code": 4001,
        }
    return result


@csrf_exempt
@render_json
def result_project(request):
    """
    Query Projcet Result Command API
    :param request:
    :return:
    """
    name = request.GET.get("project")
    page = int(request.GET.get("page", '1'))
    rows = int(request.GET.get("rows", '10'))

    if name and page > 0 and rows > 0:
        handler = Handler()
        _result = handler.query_result_by_name(name, page, rows)
        result = {
            "status": True,
            "project": name,
            "result": _result,
            "message":"Query Reuslt Succeed!",
            "code": 2001,
        }
    else:
        result = {
            "status": False,
            "project": name,
            "message": "Bad Parameters",
            "code": 4001,
        }
    return result


def test(request):
    """
    Dashboard Index Page
    :param request:
    :return:
    """
    return render_to_response("dashboard.html", {'jobs': None, 'tasks': None, 'profile': None})