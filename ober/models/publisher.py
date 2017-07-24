import logging

from django.db import models

from ober.helpers import get_cache_key

logger = logging.getLogger('miller')



class Publisher(models.Model):
  CRAWLING = 'crawling'
  READY    = 'ready'
  PREFLIGHT = 'preflight'

  STATUS_CHOICES =(
    (PREFLIGHT,   'preflight'),
    (CRAWLING,   'crawling'),
    (READY,      'ready'),
  )


  name     = models.CharField(max_length=100)
  
  url      = models.URLField(max_length=256, unique=True) # story api endpoint
  rss_url  = models.URLField(max_length=256, blank=True, null=True)

  status   = models.CharField(max_length=10, choices=STATUS_CHOICES, default=READY, db_index=True)
  
  date_last_crawled = models.DateTimeField(auto_now=True)

  def __unicode__(self):
    return '%s' % (self.name)
