from __future__ import absolute_import

import os, json
from django.core.serializers.json import DjangoJSONEncoder

from celery import group
from celery.utils.log import get_task_logger


from .celery import app

from ober.models import Publisher, Story

logger = get_task_logger('ober')

@app.task
def test(param):
    return 'The test task executed with argument "%s" ' % param



@app.task
def fetch_publishers():
  # get publisher by pk
  pubs = Publisher.objects.filter(status=Publisher.READY).values_list('pk', flat=True)

  job = group(fetch_publisher.apply_async(kwargs={
    'pk': pk
  }) for pk in pubs)

  print job.count()
  return job
  # r = requests.get(url)
  # return r.status_code

@app.task
def fetch_publisher(pk, timeout=(2.0, 30.0)):
  # get list of urls to scrape. Then stuff then change the status
  try:
    pub = Publisher.objects.get(pk=pk)
  except Publisher.DoesNotExist:
    logger.error('Publisher (pk:{0}) not found !'.format(pk))
    return None

  logger.info('Adding publisher (pk:{1}, name:{0})'.format(pub.name, pub.pk))

  pub.status = Publisher.PREFLIGHT
  pub.save()

  fetch_publisher_stories.apply_async(kwargs={
    'pk': pk
  })
  
  
  # # get latest things from 
  # pub.status = Publisher.READY
  # pub.save()

@app.task
def fetch_publisher_stories(pk, timeout=(2.0, 30.0), params=dict()):
  try:
    pub = Publisher.objects.get(pk=pk)
  except Publisher.DoesNotExist:
    logger.warning('Publisher (pk:{0}) not found !'.format(pk, Publisher.READY))
    return None
  except Exception as e:
    logger.exception(e)
    return None

  if pub.status == Publisher.KILL:
    logger.warning('Publisher (pk:{0}) crawling has been stopped (status:KILL)!'.format(pk))
    return None

  logger.info('Publisher (pk:{0}) loading endpoint: {1} ...'.format(pk, pub.endpoint))

  import requests
  from requests.exceptions import ConnectionError
  from urlparse import urlparse, parse_qs

  params.update({
    'orderby': 'date_last_modified'
  })

  if pub.date_last_updated:
    logger.warning('Publisher (pk:{0}) loading more recent than: {1} ...'.format(pk, pub.date_last_updated))
    params.update({
      'filters': json.dumps({
        'date_last_modified__gt': pub.date_last_updated
      }, cls=DjangoJSONEncoder)
    })
  

  try:
    response = requests.get(pub.endpoint, timeout=timeout, params=params)
    logger.info('Publisher (pk:{0}) loading URL: {1} ...'.format(pk, response.url))
    res = response.json()
    

  except ConnectionError as e:
    logger.exception(e)
    pub.status = Publisher.ERROR
    pub.save()
    logger.warning('Publisher (pk:{0}) unable to connect: {2}'.format(pk, e.message))
  else:
    if pub.status != Publisher.CRAWLING:
      pub.status = Publisher.CRAWLING
      pub.save()
    # get count
    logger.info('Publisher (pk:{0}, name:{1}) has {2} stories'.format(pub.pk, pub.name, res['count']))

    date_last_updated = None
    # loop results
    for _story in res['results']:
      # add form
      date_last_updated = _story[u'date_last_modified']
      print _story[u'id']
      print _story[u'short_url']
      print _story[u'date_last_modified']
      url = _story.get(u'url', os.path.join(pub.endpoint, '%s' % _story.get('id')))
      
      story, created = Story.objects.get_or_create(publisher=pub, short_url=_story[u'short_url'], defaults={
        'data': _story[u'data'],
        'title': _story.get(u'slug', ''),
        'date': _story[u'date'],
        'url': url,
        'doi': _story[u'data'].get('doi', '')
      })

      if not created:
        story.data = _story
        story.title = _story.get(u'slug', '')
        story.date = _story[u'date']
        story.url  = url
        story.doi  = _story[u'data'].get('doi', '')
        story.save()

      logger.info('Publisher (pk:{0}) story (pk:{1}) {2}'.format(pub.pk, story.pk, 'CREATED' if created else 'UPDATED'))

    if res.get('next', None):
      o = urlparse(res.get('next'))
      query = parse_qs(o.query)
      print query
      logger.info('Publisher (pk:{0}, name:{1}) has next: {2}, count: {3}'.format(pub.pk, pub.name, res.get('next'), res.get('count')))
      fetch_publisher_stories.apply_async(countdown=5, kwargs={
        'pk': pk,
        'params': query
      })
    else:

      logger.info('Publisher (pk:{0}, name:{1}) FINISHED crawling.'.format(pub.pk, pub.name))
      pub.status = Publisher.READY
      
      if date_last_updated:
        pub.date_last_updated = date_last_updated
      
      pub.save()


