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
        help = 'Loading  Project Spider to Database.'

        def add_arguments(self, parser):
            """
            add arguments
            :param parser:
            :return:
            """
            parser.add_argument('projectname', nargs='+', type=str)

        def handle(self, *args, **options):
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

                    # tmpl_path = os.path.join(settings.BASE_DIR, 'libs', 'template', 'spider.tmpl')
                    # with open(tmpl_path, 'rb') as fp:
                    #     raw = fp.read().decode('utf8')
                    # create_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    # content = string.Template(raw).substitute(CREATE_TIME=create_time,
                    #                                           PROJECTS_NAME=_projectname,
                    #                                           START_URL='http://www.example.com')

                    spider_path = os.path.join(project_path, '%s_spider.py' % (_projectname))
                    if not os.path.exists(spider_path):
                        print 'Failed to load project %s , Project does not exist! ' % (_projectname)
                    else:
                        self.load_project(spider_path)
                        print 'Successfully load project %s !' %(_projectname)

                except Exception:
                    reason =  traceback.format_exc()
                    raise CommandError('Failed to create new project %s !, Reason: %s' % (_projectname, reason))

        def load_project(self, spider_path):
            """
            Load Project File to Database
            :param spider_path: project spider path
            :return:
            """
            try:
                pass
            except Exception:
                reason = traceback.format_exc()
                raise CommandError('Failed to load project %s !, Reason: %s' % (spider_path, reason))