from datetime import datetime

from django.core.cache import cache
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.response import Response

from ober.models import Story
from ober.helpers import get_cache_key
from ober.api.pagination import VerbosePagination
from ober.api.serializers import StorySerializer
from ober.api.utils import Glue


class StoryViewSet(viewsets.ModelViewSet):
  queryset = Story.objects.all()
  serializer_class = StorySerializer
  pagination_class = VerbosePagination

  def retrieve(self, request, pk, *args, **kwargs):
  
    story = get_object_or_404(self.queryset, pk=pk)
    # get cached name
    ckey = get_cache_key(instance=story)

    if cache.has_key(ckey):
      return Response(cache.get(ckey))

    serializer = StorySerializer(story,
        context={'request': request},
    )
    d = serializer.data

    d.update({
      '_date_retrieved': datetime.now(),
      '_name': ckey
    })
    # set cached content.
    cache.set(ckey, d)

    
    return Response(d)

  def list(self, request):
    g = Glue(request=request, queryset=self.queryset)
    
    if g.warnings is not None:
      # this comes from the VerbosePagination class
      self.paginator.set_queryset_warnings(g.warnings)
      self.paginator.set_queryset_verbose(g.get_verbose_info())

    page    = self.paginate_queryset(g.queryset)
    serializer = StorySerializer(page, many=True, context={'request': request})

    # given serializer.data, get the limited ids
    # matching ids
    if g.search_query:
      ids = map(lambda x:x.get('id'), serializer.data)
      qh = Story.annotate_search_headline(query=request.query_params.get('q'), queryset=Story.objects.filter(id__in=ids))
      qh = qh.values('pk', 'search_headline', 'data')
      print dict(qh)
      # for s in qh.iterator():
      #   print s['pk'], s['search_headline'], s['data']['slug']
      #   d= mapper(serializer.data)

    return self.get_paginated_response(serializer.data)

