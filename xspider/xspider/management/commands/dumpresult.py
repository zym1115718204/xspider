#!usr/bin/env python
# -*- coding:utf-8 -*-
# Create on 2017.2.20

import os
import datetime
import string
import traceback

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from libs.handler.result_dump import ResultDump
from collector.models import Project


class Command(BaseCommand):
        help = 'Dump result from a project.'

        def add_arguments(self, parser):
            """
            add arguments
            :param parser:
            :return:
            """
            parser.add_argument('projectname', nargs='+', type=str)
            parser.add_argument('type', nargs='+', type=str)

        @staticmethod
        def handle(*args, **options):
            """
            Create New Projects Handler
            :param args:
            :param options:
            :return:
            """
            type = None
            for _type in options["type"]:
                if _type in ["json", "csv"]:
                    type = _type
                else:
                    raise CommandError("Bad Type Parameter: {0}".format(_type))

            for _projectname in options['projectname']:
                project = Project.objects(name=_projectname).first()
                if project and type=="json":
                    dump = ResultDump(project)
                    result = dump.dump_as_json()
                    return result
                elif project and type=="csv":
                    dump = ResultDump(project)
                    result = dump.dump_as_csv()
                    return result
                else:
                    CommandError("Project does not exist!:{0}".format(project.name))




                    # _projectname = _projectname.lower()

                    # project_path = os.path.join(settings.PROJECTS_PTAH, _projectname)
                    # if not os.path.exists(project_path):
                    #     os.makedirs(project_path)
                #
                #     tmpl_path = os.path.join(settings.BASE_DIR, 'libs', 'template', 'spider.tmpl')
                #     with open(tmpl_path, 'rb') as fp:
                #         raw = fp.read().decode('utf8')
                #     create_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                #     content = string.Template(raw).substitute(CREATE_TIME=create_time,
                #                                               PROJECTS_NAME=_projectname,
                #                                               START_URL='http://www.example.com')
                #
                #     spider_path = os.path.join(project_path, '%s_spider.py' % (_projectname))
                #     if not os.path.exists(spider_path):
                #         with open(spider_path, 'w') as fp:
                #             fp.write(content.encode('utf8'))
                #         print 'Successfully create a new project %s !' %(_projectname)
                #     else:
                #         print 'Failed to create project %s , Project already exists! ' %(_projectname)
                #
                #     tmpl_path = os.path.join(settings.BASE_DIR, 'libs', 'template', 'models.tmpl')
                #     with open(tmpl_path, 'rb') as fp:
                #         raw = fp.read().decode('utf8')
                #     create_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                #     content = string.Template(raw).substitute(CREATE_TIME=create_time,
                #                                               PROJECTS_NAME=_projectname,
                #                                               PROJECTS_NAME_TASK=str(_projectname).capitalize() + 'Task',
                #                                               PROJECTS_NAME_RESULT=str(_projectname).capitalize() + 'Result')
                #
                #     models_path = os.path.join(project_path, '%s_models.py' % (_projectname))
                #     if not os.path.exists(models_path):
                #         with open(models_path, 'w') as fp:
                #             fp.write(content.encode('utf8'))
                #         print 'Successfully create a new project models %s !' %(models_path)
                #     else:
                #         print 'Failed to create project %s , Project already exists! ' %(models_path)
                #
                # except Exception:
                #     reason =  traceback.format_exc()
                #     raise CommandError('Failed to create new project %s !, reason: %s' % (_projectname, reason))
