from django.contrib import admin
from .models import VideoModel

# Register your models here.
@admin.register(VideoModel)
class VideoAdmin(admin.ModelAdmin):
    pass