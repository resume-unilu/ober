from django.contrib import admin
from ober.models import Story, Publisher



class StoryAdmin(admin.ModelAdmin):
  # inlines = (CaptionInline,)
  exclude=[]


class PublisherAdmin(admin.ModelAdmin):
  list_display = ('name', 'endpoint', 'status', 'date_last_updated')
  prepopulated_fields = {"slug": ("name",)}



admin.site.register(Story, StoryAdmin)

admin.site.register(Publisher, PublisherAdmin)