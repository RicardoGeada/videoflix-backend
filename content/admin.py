from django.contrib import admin
from .models import VideoModel, GenreModel

# Register your models here.
@admin.register(VideoModel)
class VideoAdmin(admin.ModelAdmin):
    pass

@admin.register(GenreModel)
class GenreAdmin(admin.ModelAdmin):
    pass