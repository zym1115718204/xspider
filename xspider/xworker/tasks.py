from __future__ import absolute_import
from collector.utils import *
from celery import shared_task


@shared_task
def add(x, y):
    return x + y


@shared_task
def generator(project_id):
    """
    Celery Generator Task
    :return:
    """
    generator = Generator(project_id)
    result = generator.run_generator()
    return result


@shared_task
def processor(task):
    """
    Celery Processor Task
    :return:
    """
    processor = Processor(task_id)
    result = processor.run_processor()
    return result