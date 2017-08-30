#!/usr/bin/env python
# -*- coding: utf-8 -*-
# special tasks for biographical data
import logging

from ober.management.commands.task import Command as TaskCommand
from ober.models import Story

logger = logging.getLogger('console')


class Command(TaskCommand):
  """
  Usage sample: 
  python manage.py story update_search_vector --pk=991
  """
  help = 'A lot of tasks dealing with Stories, ngrams and Postgres vectors'
  

  available_tasks = (
    'update_search_vector',
    'search'
  )


  def add_arguments(self, parser):
    super(Command, self).add_arguments(parser)
    parser.add_argument(
        '--query',
        dest='query',
        default=None,
        help='query for search vectors',
    )


  def search(self, pk=None, query=None, **options):
    q = Story.get_search_Q(query)

    stories = Story.objects.filter(q)
    logger.debug('search query:  {0}'.format(query))
    logger.debug('total results: {0}'.format(stories.count()))

    ids = []
    for story in stories[:10].iterator():
      ids.append(story.id)

    results = Story.annotate_search_headline(query=query, queryset=Story.objects.filter(id__in=ids))

    for story in results.iterator():
      print(u'\n . {0} - {1}'.format(story.pk, story.title))
      print(u'   {0}'.format(story.search_headline))
      


  def update_search_vector(self, pk=None, model=False, **options):
    logger.debug('task: update_search_vectors')

    stories = Story.objects.all()
    if pk:
      stories = stories.filter(pk=pk)
    for story in stories.iterator():
      logger.debug('performing: update_search_vectors for story {pk:%s, titla:%s}' % (story.pk, story.title))
      story.update_search_vector()
      

  

