#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.20

import os
import datetime
import string
import traceback

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from manager.manager import SmartProxyPool

class Command(BaseCommand):

        @staticmethod
        def handle(*args, **options):
            """
            Update proxies ip to reids/10
            :return:
            """
            smartproxy = SmartProxyPool()
            smartproxy.update_redis_proxies_ip_pool()


