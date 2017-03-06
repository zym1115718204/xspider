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
        help = 'Run Xspider Celery Flower.'

        @staticmethod
        def handle(*args, **options):
            """
            Run Xspider Celert Flower Dashboard
            :param args:
            :param options:
            :return:
            """
            try:
                subprocess.call("celery -A xspider flower", shell=True)

            except Exception:
                reason =  traceback.format_exc()
                raise CommandError('Failed to run celery flower! Reason: %s' % (reason))
