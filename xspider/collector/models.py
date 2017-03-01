#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.20
from __future__ import unicode_literals

import datetime
from mongoengine import *
from django.db import models


# Create your models here.
class Project(Document):
    (STATUS_OFF, STATUS_ON, STATUS_DEBUG, STATUS_DELAY) = range(0, 4)
    STATUS_CHOICES = ((STATUS_OFF, u"下线"), (STATUS_ON, u"启用"), (STATUS_DEBUG, u'调试'), (STATUS_DELAY, u'过期'))
    (PRIOR_0, PRIOR_1, PRIOR_2, PRIOR_3, PRIOR_4, PRIOR_5, PRIOR_6) = range(-1, 6)
    PRIOR_CHOICES = ((PRIOR_0, u"-1"),
                     (PRIOR_1, u"0"),
                     (PRIOR_2, u"1"),
                     (PRIOR_3, u"2"),
                     (PRIOR_4, u"3"),
                     (PRIOR_5, u"4"),
                     (PRIOR_6, u"5"), )
    name = StringField(max_length=128)
    status = IntField(default=STATUS_DEBUG, choices=STATUS_CHOICES)
    priority = IntField(default=PRIOR_6, choices=PRIOR_CHOICES)
    info = StringField(max_length=1024)
    update_datetime = DateTimeField(default=datetime.datetime.now)
    script = StringField(max_length=102400)
    models = StringField(max_length=10240)
    generator_interval = StringField(max_length=20)
    last_generator_time = DateTimeField()
    downloader_interval = StringField(max_length=20)
    downloader_dispatch = IntField(default=60)
    meta = {
        "db_alias": "xspider_project",
        "indexes": [
            "name"
        ]
    }


class Task(Document):
    (STATUS_LIVE, STATUS_DISPATCH, STATUS_PROCESS, STATUS_FAIL, STATUS_SUCCESS, STATUS_INVALID) = range(0, 6)
    STATUS_CHOICES = ((STATUS_LIVE, u"新增"),
                      (STATUS_DISPATCH, u'分发中'),
                      (STATUS_PROCESS, u"进行中"),
                      (STATUS_FAIL, u"下载失败"),
                      (STATUS_SUCCESS, u"下载成功"),
                      (STATUS_INVALID, u"任务失效"),)

    project = ReferenceField(Project, reverse_delete_rule=CASCADE)
    status = IntField(default=STATUS_LIVE, choices=STATUS_CHOICES)
    task_id = StringField(max_length=120)
    update_time = DateTimeField(default=datetime.datetime.now)
    schedule = StringField(max_length=1024)
    url = StringField(max_length=8000)
    args = StringField(max_length=2048, null=True)  # 存储cookie， header等信息
    info = StringField(max_length=2048, null=True)  # 源数据的信息,如数据分类,公司名称,权限等
    retry_times = IntField(default=0)
    callback = StringField(max_length=120)
    track_log = StringField(max_length=10240)
    spend_time = StringField(max_length=120, default='0')
    meta = {
        "allow_inheritance": True,
        "db_alias": "xspider_task",
        "indexes": ["task_id", "url", "status"],
    }  # 默认连接的数据库


class Result(Document):
    project = ReferenceField(Project)
    task = ReferenceField(Task)
    url = StringField(max_length=256)
    update_datetime = DateTimeField(default=datetime.datetime.now)
    result = StringField(max_length=10240)
    meta = {
        "db_alias": "xspider_result",
        "indexes": ["task"]
    }    # 默认连接的数据库
