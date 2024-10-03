from .models import VideoModel
from django.dispatch import receiver
from django.db.models.signals import post_delete
import os
import shutil

@receiver(post_delete, sender= VideoModel)
def video_post_delete(sender, instance, **kwargs):
    if instance.video_file:
        
        folder_path = os.path.dirname(instance.video_file.path)
        
        if os.path.isdir(folder_path):
            try:
                shutil.rmtree(folder_path)  # delete folder and content
            except OSError as e:
                print(f"Error: {folder_path} : {e.strerror}")