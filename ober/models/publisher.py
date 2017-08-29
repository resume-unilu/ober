import logging

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from ober.helpers import get_cache_key
from ober.consumers import broadcast

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

  
  def __init__(self, *args, **kwargs):
    """
    Store original values internally.
    used in Story method `dispatch_status_changed`
    """
    super(Publisher, self).__init__(*args, **kwargs)
    self._original = {
      'status': self.status
    }

  def __unicode__(self):
    return '%s' % (self.name)



@receiver(post_save, sender=Publisher)
def broadcast_publisher_info(sender, instance, created, **kwargs):
  """
  use django channels to breadcast information 
  """
  if created:
    # notify creation to generic channel
    broadcast('pulse', {
      'status': instance.status,
      'pk': instance.pk,
      'slug': instance.slug,
      'date_last_crawled': '{0}'.format(instance.date_last_crawled)
    }, event_type=settings.OBER_EVENTS_CREATE_PUBLISHER)
  else:
    # notify updates, with basic serialized instance
    broadcast('pulse', {
      'status': instance.status,
      'status_changed': instance.status != instance._original.get('status'),
      'pk': instance.pk,
      'slug': instance.slug,
      'date_last_crawled': '{0}'.format(instance.date_last_crawled)
    }, event_type=settings.OBER_EVENTS_UPDATE_PUBLISHER)