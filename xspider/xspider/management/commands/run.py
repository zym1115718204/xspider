#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.20

import os
import datetime
import string
import traceback
import threading
import multiprocessing
import subprocess

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from scheduler.scheduler import XspiderScheduler

HELP = """
Run Xspider Background.
Usage: python manage.py run {all/web/flower/generator/processor}
    all:         Run xspider all modules.
    web:         Run xspider web modules.
    flower:      Run xspider celery flower.
    generator:   Run xspider celery generator workers.
    processor:   Run xspider celery processor workers.
"""


class RunXspider(object):
    """
    Run Xspider
    """
    @staticmethod
    def runweb():
        """
        Run celery generator, flower and processor
        :return:
        """
        try:
            subprocess.call("python manage.py runserver 2017", shell=True)

        except Exception:
            reason = traceback.format_exc()
            raise CommandError('Failed to run web! Reason: %s' % (reason))

    @staticmethod
    def runscheduler():
        """
        Run celery generator, flower and processor
        :return:
        """
        try:
            scheduler = XspiderScheduler()
            scheduler.run()

        except Exception:
            reason = traceback.format_exc()
            raise CommandError('Failed to run scheduler! Reason: %s' % (reason))

    @staticmethod
    def runflower():
        """
        Run celery generator, flower and processor
        :return:
        """
        try:
            subprocess.call("celery -A xspider flower", shell=True)

        except Exception:
            reason = traceback.format_exc()
            raise CommandError('Failed to run celery flower! Reason: %s' % (reason))

    @staticmethod
    def rungenerator():
        """
        Run celery generator, flower and processor
        :return:
        """
        try:
            subprocess.call("celery worker --app=xspider -l info -n worker1@%h -Q low-generator", shell=True)

        except Exception:
            reason = traceback.format_exc()
            raise CommandError('Failed to run celery worker! Reason: %s' % (reason))

    @staticmethod
    def runprocessor():
        """
        Run celery generator, flower and processor
        :return:
        """

        try:
            subprocess.call("celery worker --app=xspider -l info -n worker2@%h -Q low-processor", shell=True)

        except Exception:
            reason = traceback.format_exc()
            raise CommandError('Failed to run celery worker! Reason: %s' % (reason))

    def _run(self, cmd):
        """
        add run command to process
        :return:
        """
        t = multiprocessing.Process(target=cmd)
        t.daemon = True
        t.start()

    def run(self, command):
        """
        Run Scheduler
        :return:
        """
        try:
            if command == "all":
                self._run(self.runweb)
                self._run(self.rungenerator)
                self._run(self.runprocessor)
                self._run(self.runflower)
                self._run(self.runscheduler)

            elif command == "web":
                self._run(self.runweb)
            elif command == "flower":
                self._run(self.runflower)
            elif command == "generator":
                self._run(self.rungenerator)
            elif command == "processor":
                self._run(self.runprocessor)
            elif command == "scheduler":
                self._run(self.runscheduler)
            else:
                raise CommandError("error: too few arguments. {all/web/flower/generator/processor}")

            while True:
                pass

        except KeyboardInterrupt:
            print "Xspider Stoped."

        except Exception:
            reason = traceback.format_exc()
            raise CommandError('Failed to run xspider! Reason: %s' % (reason))


class Command(BaseCommand):
        help = """
        Run Xspider Background Management.
        Usage: python manage.py run {all/web/flower/generator/processor}
        """

        def add_arguments(self, parser):
            """
            add arguments
            :param parser:
            :return:
            """
            print HELP
            parser.add_argument('command', nargs='+', type=str)

        @staticmethod
        def handle(*args, **options):
            """
            Run Xspider Background Management
            :param args:
            :param option
            :return:
            """
            cmd = options["command"][0]
            if cmd in ['all', "web", 'generator', 'processor', 'flower']:
                xspider = RunXspider()
                xspider.run(cmd)
            else:
                print HELP
                raise CommandError("error: too few arguments. {all/web/flower/generator/processor}")

