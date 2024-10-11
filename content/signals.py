from .models import VideoModel
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from .tasks import convert_to_hls, delete_file, create_master_playlist
import os
import shutil
import django_rq

@receiver(post_delete,sender= VideoModel)
def video_post_delete(sender, instance, **kwargs):
    if instance.video_file or instance.thumbnail_img:
        
        folder_path = os.path.join('media', 'videos', str(instance.pk))
        
        if os.path.isdir(folder_path):
            try:
                shutil.rmtree(folder_path)  # delete folder and content
            except OSError as e:
                print(f"Error: {folder_path} : {e.strerror}")
                

@receiver(post_save,sender=VideoModel)
def video_post_save(sender, instance, created, **kwargs):
    if created and instance.video_file:
            queue = django_rq.get_queue('default', autocommit=True)
            job_480 = queue.enqueue(convert_to_hls, instance, resolution='480')
            job_720 = queue.enqueue(convert_to_hls, instance, resolution='720', depends_on=job_480)
            job_1080 = queue.enqueue(convert_to_hls, instance, resolution='1080', depends_on=job_720)
            queue.enqueue(delete_file, instance.video_file.path, depends_on=job_1080)
            queue.enqueue(create_master_playlist, instance, depends_on=job_1080)
