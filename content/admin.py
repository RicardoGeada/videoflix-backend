from django.contrib import admin
from .models import VideoModel, GenreModel
from import_export import resources
from import_export.admin import ImportExportModelAdmin

# Register your models here.
@admin.register(VideoModel)
class VideoAdmin(ImportExportModelAdmin):
    pass

@admin.register(GenreModel)
class GenreAdmin(ImportExportModelAdmin):
    pass


class VideoResource(resources.ModelResource):
    class Meta:
        model = VideoModel
        

class GenreResource(resources.ModelResource):
    
    class Meta:
        model = GenreModel