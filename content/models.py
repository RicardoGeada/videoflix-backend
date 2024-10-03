from django.db import models
from datetime import date
from .utils import video_upload_path
from django.db.models.signals import post_save

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
        is_new = self.id is None

        if not self.id:
            saved_file = self.video_file
            self.video_file = None  
            super().save(*args, **kwargs)  
            self.video_file = saved_file 

        super().save(*args, **kwargs)
        
        if is_new:
            post_save.send(sender=self.__class__, instance=self, created=True)