#!/usr/bin/env python
# -*- coding: utf-8 -*-


from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^test$', views.test),
    url(r'^time/$', views.test_current_datetime),
]