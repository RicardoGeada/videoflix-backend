from .models import VideoModel
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from .tasks import convert_480p
import os
import shutil

@receiver(post_delete,sender= VideoModel)
def video_post_delete(sender, instance, **kwargs):
    if instance.video_file:
        
        folder_path = os.path.dirname(instance.video_file.path)
        
        if os.path.isdir(folder_path):
            try:
                shutil.rmtree(folder_path)  # delete folder and content
            except OSError as e:
                print(f"Error: {folder_path} : {e.strerror}")
                

@receiver(post_save,sender=VideoModel)
def video_post_save(sender, instance, created, **kwargs):
    if created and instance.video_file:
            convert_480p(instance.video_file.path)
  