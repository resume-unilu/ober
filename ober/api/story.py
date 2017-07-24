from datetime import datetime

from django.core.cache import cache
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.response import Response

from ober.models import Story
from ober.helpers import get_cache_key
from ober.api.serializers import StorySerializer


class StoryViewSet(viewsets.ModelViewSet):
  queryset = Story.objects.all()
  serializer_class = StorySerializer


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