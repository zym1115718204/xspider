# -*- coding: utf-8 -*-
from __future__ import absolute_import
#import celery
from celery import Celery
app = Celery('task')                                # 创建 Celery 实例
app.config_from_object('xworker.celeryconfig')   # 通过 Celery 实例加载配置模块

