#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.20

import os
import datetime
import string
import traceback
import subprocess

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
        help = 'Run Xspider Celery Generator Worker.'

        @staticmethod
        def handle(*args, **options):
            """
            Run Xspider Celery Generator Worker
            :param args:
            :param options:
            :return:
            """

            try:
                subprocess.call("celery worker --app=xspider -l info -n worker1@%h -Q low-generator", shell=True)

            except Exception:
                reason =  traceback.format_exc()
                raise CommandError('Failed to run celery worker! Reason: %s' % (reason))
