#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.20

import os
import datetime
import string
import traceback

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
        help = 'Start a new project for xspider.'

        def add_arguments(self, parser):
            """
            add arguments
            :param parser:
            :return:
            """
            parser.add_argument('projectname', nargs='+', type=str)

        @staticmethod
        def handle(*args, **options):
            """
            Create New Projects Handler
            :param args:
            :param options:
            :return:
            """
            for _projectname in options['projectname']:
                try:
                    project_path = os.path.join(settings.PROJECTS_PTAH, _projectname)
                    if not os.path.exists(project_path):
                        os.makedirs(project_path)

                    tmpl_path = os.path.join(settings.BASE_DIR, 'libs', 'template', 'spider.tmpl')
                    with open(tmpl_path, 'rb') as fp:
                        raw = fp.read().decode('utf8')
                    create_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    content = string.Template(raw).substitute(CREATE_TIME=create_time,
                                                              PROJECTS_NAME=_projectname,
                                                              START_URL='http://www.example.com')

                    spider_path = os.path.join(project_path, '%s_spider.py' % (_projectname))
                    if not os.path.exists(spider_path):
                        with open(spider_path, 'w') as fp:
                            fp.write(content.encode('utf8'))
                        print 'Successfully create a new project %s !' %(_projectname)
                    else:
                        print 'Failed to create project %s , Project already exists! ' %(_projectname)

                except Exception:
                    reason =  traceback.format_exc()
                    raise CommandError('Failed to create new project %s !, reason: %s' % (_projectname, reason))
