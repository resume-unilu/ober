from __future__ import absolute_import

from celery import group
from .celery import app

from ober.models import Publisher, Story

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
def fetch_publisher(pk):
  # get list of urls to scrape. Then stuff then change the status
  try:
    pub = Publisher.objects.get(pk=pk, status=Publisher.READY)
  except Publisher.DoesNotExist:
    return None

  pub.status = Publisher.PREFLIGHT
  pub.save()
  print 'DONE'


