from rest_framework import serializers
from ober.models import Story, Publisher


class PublisherSerializer(serializers.ModelSerializer):
  class Meta:
    model = Publisher
    fields = ('id', 'name', 'slug')


class StorySerializer(serializers.ModelSerializer):
  publisher = PublisherSerializer()

  class Meta:
    model = Story
    fields = ('id', 'short_url', 'title', 'data', 'publisher')