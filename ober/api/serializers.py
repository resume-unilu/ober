from rest_framework import serializers
from ober.models import Story


class StorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Story
    fields = ('id', 'short_url', 'title', 'data')