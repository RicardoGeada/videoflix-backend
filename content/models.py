from django.db import models
from datetime import date
from .utils import video_upload_path

# Create your models here.
class VideoModel(models.Model):
    
    created_at = models.DateField(default=date.today)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=500)
    video_file = models.FileField(upload_to=video_upload_path, blank=True, null=True)
    
    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videos"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):

        if not self.id:
            saved_file = self.video_file
            self.video_file = None  
            super().save(*args, **kwargs)  
            self.video_file = saved_file 

        super().save(*args, **kwargs)