#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create : 2017.2.20

import os
import traceback

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
        help = 'Start a new project for xspider.'

        def add_arguments(self, parser):
            parser.add_argument('projectname', nargs='+', type=str)

        def handle(self, *args, **options):
            for _projectname in options['projectname']:
                try:
                    print settings.BASE_DIR, settings.PROJECTS_PTAH
                    spider_path = os.path.join(settings.PROJECTS_PTAH, _projectname)
                    if not os.path.exists(spider_path):
                        os.makedirs(spider_path)

                    print 'Successfully create a new project %s '%(_projectname)
                except Exception:
                    print traceback.format_exc()
                    raise CommandError('Failed to create new project %s' % (_projectname))
