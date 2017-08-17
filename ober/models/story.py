#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.search import SearchVectorField

from django.core.cache import cache

from django.db import models
from django.db.models.signals import pre_delete, post_save, pre_save
from django.dispatch import receiver

from ober.helpers import get_cache_key

from ober.models import Publisher


logger = logging.getLogger('miller')



class Story(models.Model):
  # simple identifier
  title     = models.CharField(max_length=500)
  # remote location
  url       = models.CharField(max_length=256, unique=True)
  # doi identifier, if any, e.g doi.org/10.25517/86fuhN8-1987
  doi       = models.URLField(max_length=100, blank=True, null=True)
  # original shorturl
  short_url = models.CharField(max_length=22, db_index=True)
  # story data: titles etc..
  data      = JSONField(verbose_name=u'metadata contents', help_text='JSON format', default=dict(), blank=True)
  # date displayed (metadata)
  date               = models.DateTimeField(db_index=True, blank=True, null=True) 
  date_created       = models.DateTimeField(auto_now_add=True)
  date_last_modified = models.DateTimeField(auto_now=True)

  # add huge search field
  search_vector = SearchVectorField(null=True, blank=True)
  # publisher!
  publisher = models.ForeignKey(Publisher, related_name='stories', blank=True, null=True, on_delete=models.CASCADE)

  def __unicode__(self):
    return '%s - %s' % (self.title, self.doi)

  class Meta:
    ordering = ('-date_last_modified',)
    verbose_name_plural = 'stories'
    unique_together = (('publisher', 'short_url'),)
    

  @staticmethod
  def get_search_Q(query, raw=False):
    """
    Return search queryset for this model, ranked by weight. Check update_search_vector function for more info
    """
    from ober.postgres import RawSearchQuery
    #' & '.join(map(lambda x: x if x.endswith(':*') else '%s:*' % x, query.split(' ')))
    return models.Q(search_vector=RawSearchQuery(query, config='simple'))


@receiver(pre_save, sender=Story)
def clear_cache_on_save(sender, instance, **kwargs):
  """
  Clean current story from cache.
  """
  if getattr(instance, '_dirty', None) is not None:
    return
  # ckey = # 'story.%s' % instance.short_url
  cache.delete_pattern('%s*' % get_cache_key(instance))
  logger.debug('story@pre_save {pk:%s, short_url:%s} cache deleted.' % (instance.pk,instance.short_url))



@receiver(pre_delete, sender=Story)
def delete_cache_on_save(sender, instance, **kwargs):
  cache.delete_pattern('%s*' % get_cache_key(instance))
  logger.debug('story@pre_delete {pk:%s} delete_cache_on_save: done' % instance.pk)
