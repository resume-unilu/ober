from rest_framework import serializers
from ober.models import Story, Publisher


class LitePublisherSerializer(serializers.ModelSerializer):
  class Meta:
    model = Publisher
    fields = ('id', 'name', 'slug')

class PublisherSerializer(serializers.ModelSerializer):
  class Meta:
    model = Publisher
    fields = ('id', 'name', 'slug', 'status', 'endpoint', 'date_last_crawled', 'date_last_updated')


class StorySerializer(serializers.ModelSerializer):
  publisher = LitePublisherSerializer()

  class Meta:
    model = Story
    fields = ('id', 'short_url', 'title', 'data', 'publisher')