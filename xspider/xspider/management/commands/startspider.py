from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
        help = 'Start a new project for xspider.'

        def add_arguments(self, parser):
            parser.add_argument('projectname', nargs='+', type=str)

        def handle(self, *args, **options):
            for _projectname in options['projectname']:
                try:
                    print 'Successfully create a new project %s '%(_projectname)
                except:
                    raise CommandError('Failed to create new project %s' % (_projectname))
