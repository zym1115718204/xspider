#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.20

import os
import datetime
import string
import traceback

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from scheduler.scheduler import XspiderScheduler


class Command(BaseCommand):
        help = 'Run Xspider Scheduler.'

        @staticmethod
        def handle(*args, **options):
            """
            Run Xspider Scheduler
            :param args:
            :param options:
            :return:
            """

            try:
               scheduler = XspiderScheduler()
               scheduler.run()

            except Exception:
                reason =  traceback.format_exc()
                raise CommandError('Failed to run scheduler! Reason: %s' %(reason))
