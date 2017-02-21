from __future__ import unicode_literals

from django.db import models
from mongoengine import *

# Create your models here.
class Project(Document):
    (STATUS_ON, STATUS_OFF) = range(1, 3)
    STATUS_CHOICES = ((STATUS_ON, u"启用"), (STATUS_OFF, u"下线"), )
    (PRIOR_0, PRIOR_1, PRIOR_2, PRIOR_3, PRIOR_4, PRIOR_5, PRIOR_6) = range(-1, 6)
    PRIOR_CHOICES = ((PRIOR_0, u"-1"),
                     (PRIOR_1, u"0"),
                     (PRIOR_2, u"1"),
                     (PRIOR_3, u"2"),
                     (PRIOR_4, u"3"),
                     (PRIOR_5, u"4"),
                     (PRIOR_6, u"5"), )
    name = StringField(max_length=128)
    status = IntField(default=STATUS_ON, choices=STATUS_CHOICES)
    priority = IntField(default=PRIOR_6, choices=PRIOR_CHOICES)
    info = StringField(max_length=1024)
    update_datetime = DateTimeField(default=datetime.datetime.now)
    script = StringField(max_length=40960)
    generator_interval = StringField(max_length=20)
    downloader_interval = StringField(max_length=20)
    meta = {
        "db_alias": "xspider_source",
        "indexes": [
            "name"
        ]
    }

class Task(Document):
    (STATUS_LIVE, STATUS_DISPATCH, STATUS_PROCESS, STATUS_FAIL, STATUS_SUCCESS, STATUS_INVALID) = range(1, 7)
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
    args = StringField(max_length=2048, null=True)    # 存储cookie， header等信息
    info = StringField(max_length=2048, null=True)    # 源数据的信息,如数据分类,公司名称,权限等
    retry_times = IntField(default=0)
    track_log = StringField(max_length=10240)
    meta = {
        "db_alias": "xspider_task",
        "indexes": ["status", [("project", 1), ("status", 1)], [("project", 1), ("status", 1), ("url", 1)]],
    }    # 默认连接的数据库

class Result(Document):
    project = ReferenceField(Project)
    task = ReferenceField(Task)
    url = StringField(max_length=256)
    update_datetime = DateTimeField(default=datetime.datetime.now)
    result = StringField(max_length=10240)
    meta = {
        "db_alias": "xspider_result",
        "indexes": ["task", [("project", 1), ("task", 1)]]
    }    # 默认连接的数据库
