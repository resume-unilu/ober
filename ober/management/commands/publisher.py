#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ober.management.commands.task import Command as Taskcommand
from ober.models import Publisher, Story
from ober.tasks import fetch_publisher

class Command(Taskcommand):
  """
  Usage sample: 
  python manage.py publisher crawl --pk=991
  """
  help = 'A lot of tasks dealing with Publishers celery tasks'

  available_tasks = (
    'crawl',
    'kill',
    'simulate_crawl'
  )

  def crawl(self, pk, **options):
    qpk = {'pk': pk} if pk.isdigit() else {'slug': pk}
    pub = Publisher.objects.get(**qpk)
    if pub.status == Publisher.KILL:
      pub.status = Publisher.READY
      pub.save()
    result = fetch_publisher.delay(pk=pub.pk)

  def simulate_crawl(self, pk, **options):
    qpk = {'pk': pk} if pk.isdigit() else {'slug': pk}
    pub = Publisher.objects.get(**qpk)
    if pub.status == Publisher.READY:
      pub.status = Publisher.CRAWLING;
      pub.save()
    from time import sleep
    sleep(5)
    pub.status = Publisher.READY;
    pub.save()


  def kill(self, pk, **options):
    qpk = {'pk': pk} if pk.isdigit() else {'slug': pk}
    pub = Publisher.objects.get(**qpk)

    pub.status= Publisher.KILL
    pub.save()
    