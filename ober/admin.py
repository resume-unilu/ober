from django.contrib import admin
from ober.models import Story, Publisher



class StoryAdmin(admin.ModelAdmin):
  # inlines = (CaptionInline,)
  exclude=[]



admin.site.register(Story, StoryAdmin)

admin.site.register(Publisher)