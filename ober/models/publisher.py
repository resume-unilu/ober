import logging

from django.db import models

from ober.helpers import get_cache_key

logger = logging.getLogger('miller')



class Publisher(models.Model):
  CRAWLING  = 'crawling'
  ERROR     = 'error' # connection error
  READY     = 'ready'
  PREFLIGHT = 'preflight'
  KILL      = 'kill' # order to stop the execution

  STATUS_CHOICES = (
    (PREFLIGHT,   'preflight'),
    (CRAWLING,   'crawling'),
    (READY,      'ready'),
    (ERROR,      'error'),
  )


  name     = models.CharField(max_length=100)
  slug     = models.SlugField(max_length=50, unique=True)
  
  endpoint = models.URLField(max_length=256, unique=True) # api/ endpoint

  status   = models.CharField(max_length=10, choices=STATUS_CHOICES, default=READY, db_index=True)
  
  date_last_crawled = models.DateTimeField(auto_now=True)
  date_last_updated = models.DateTimeField(blank=True, null=True)

  def __unicode__(self):
    return '%s' % (self.name)
