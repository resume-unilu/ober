#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Tasks on models
import logging, time
from django.core.management.base import BaseCommand

logger = logging.getLogger('console')

class Command(BaseCommand):
  """
  Usage sample: 
  python manage.py task crawl --pk=991
  """
  help = 'Base tasks manager'
  
  available_tasks = ()


  def add_arguments(self, parser):
    parser.add_argument('taskname')

    parser.add_argument(
      '--pk',
      dest='pk',
      default=None,
      help='primary key of the instance',
    )

    parser.add_argument(
      '--model',
      dest='model',
      default=False,
      help='model name',
    )

    parser.add_argument(
        '--user',
        dest='user',
        default=False,
        help='ober username, if requested.',
    )

  def handle(self, *args, **options):
    start = time.time()
    if options['taskname'] in self.available_tasks:
      getattr(self, options['taskname'])(**options)
    else:
      logger.debug('command NOT FOUND, tasks availables: ["%s"]' % '","'.join(self.available_tasks))
    end = time.time()
    logger.debug('command finished in %s seconds.' % (end - start))
 