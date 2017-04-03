#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.20

import os
import sys
import datetime
import string
import traceback
import threading
import multiprocessing
import subprocess


from subprocess import Popen, PIPE

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
            # p = Popen("python manage.py runserver 2017",shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            # output, err = p.communicate(b"input data that is passed to subprocess' stdin")
            # rc = p.returncode

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
        process = multiprocessing.Process(target=cmd)
        process.daemon = True
        process.start()
        return process

    def run(self, command):
        """
        Run Scheduler
        # Todo: Use threading or multiprocessing will make cpu usage to 100%s
        :return:
        """
        threads = []
        try:
            if command == "all":
                process_1 = self._run(self.runweb)
                process_2 = self._run(self.rungenerator)
                process_3 = self._run(self.runprocessor)
                process_4 = self._run(self.runflower)
                process_5 = self._run(self.runscheduler)

                process_1.join()
                process_2.join()
                process_3.join()
                process_4.join()
                process_5.join()

            if command == "dev":
                # process_1 = self._run(self.runweb)
                process_2 = self._run(self.rungenerator)
                process_3 = self._run(self.runprocessor)
                # process_4 = self._run(self.runflower)
                process_5 = self._run(self.runscheduler)

                # process_1.join()
                process_2.join()
                process_3.join()
                # process_4.join()
                process_5.join()

            elif command == "web":
                process = self._run(self.runweb)
                process.join()
                # self.runweb()
            elif command == "flower":
                process = self._run(self.runflower)
                process.join()
                # self.runflower()
            elif command == "generator":
                process = self._run(self.rungenerator)
                process.join()
                # self.rungenerator()
            elif command == "processor":
                process = self._run(self.runprocessor)
                process.join()
            elif command == "scheduler":
                process = self._run(self.runscheduler)
                process.join()
            else:
                raise CommandError("error: too few arguments. {all/web/flower/generator/processor}")

        except KeyboardInterrupt:
            print "Xspider Stoped."

        except Exception:
            reason = traceback.format_exc()
            raise CommandError('Failed to run xspider! Reason: %s' % (reason))


class Command(BaseCommand):
        help = """
        Run Xspider Background.
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
            if cmd in ['all', "web", 'scheduler', 'generator', 'processor', 'flower','dev']:
                xspider = RunXspider()
                xspider.run(cmd)
            else:
                print HELP
                raise CommandError("error: too few arguments. {all/web/flower/generator/processor}")

