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


  def update_search_vector(self):
    """
    Fill the search_vector using self.data:
    e.g. get data['title'] if is a basestring or data['title']['en_US'] according to the values contained into settings.LANGUAGES
    Note that a language configuration can be done as well, in this case consider the last value in settings.LANGUAGES (e.g. 'english')
    Then fill search_vector with authors and tags.
    """
    from django.db import connection
    from django.conf import settings
    from pydash import py_

    fields = (('title', 'A'), ('abstract', 'B'))
    contents = []

    _metadata = self.data.get('data')

    for _field, _weight in fields:
      default_value = _metadata.get(_field, None)
      value = u"\n".join(filter(None,[
        default_value if isinstance(default_value, basestring) else None
      ] + list(
        set(
          py_.get(_metadata, '%s.%s' % (_field, lang[2]), None) for lang in settings.LANGUAGES)
        )
      ))
      if value:
        contents.append((value, _weight, 'simple'))
    
    authors   =  u", ".join([u'%s - %s' % (t.get('fullname',''), t.get('affiliation','')) for t in self.data.get('authors', [])])
    
    # # well, quite complex.
    tags      =  u", ".join(set(filter(None, py_.flatten([ 
      [py_.get(tag.get('data'), 'name.%s' % lang[2], None) for lang in settings.LANGUAGES] + [tag.get('slug'), tag.get('name')] for tag in self.data.get('tags', [])
    ]))))

    # 
    if authors:
      contents.append((authors, 'A', 'simple'))
    if tags:
      contents.append((tags, 'C', 'simple'))

    # contents.append((u"\n".join(BeautifulSoup(markdown(u"\n\n".join(filter(None,[
    #     self.contents,
    #   ])), extensions=['footnotes'])).findAll(text=True)), 'B', 'simple'))
    
    q = ' || '.join(["setweight(to_tsvector('simple', COALESCE(%%s,'')), '%s')" % weight for value, weight, _config in contents])

    # print contents

    with connection.cursor() as cursor:
      cursor.execute(''.join(["""
        UPDATE ober_story SET search_vector = x.weighted_tsv FROM (  
          SELECT id,""",
            q,
          """
                AS weighted_tsv
            FROM ober_story
          WHERE ober_story.id=%s
        ) AS x
        WHERE x.id = ober_story.id
      """]), [value for value, _w, _c in contents] +  [self.id])

    logger.debug('story {pk:%s, title:%s} search_vector updated.'%(self.pk, self.title))
    
    return contents

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
