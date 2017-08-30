from rest_framework import viewsets
from ober.models import Publisher
from ober.api.pagination import VerbosePagination
from ober.api.serializers import PublisherSerializer


class PublisherViewSet(viewsets.ModelViewSet):
  queryset = Publisher.objects.all()
  serializer_class = PublisherSerializer
  pagination_class = VerbosePagination