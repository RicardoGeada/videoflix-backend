import os

def video_upload_path(instance, filename):
    """
    Generates a file path for uploaded video files.
    The path includes the ID of the instance to ensure unique storage directories.
    """
    return f'videos/{instance.pk}/{filename}'


def thumbnail_upload_path(instance, filename):
    """
    Generates a file path for uploaded thumbnails and renames the file 'thumbnail'.
    """
    video_folder = f'videos/{instance.pk}'
    
    ext = os.path.splitext(filename)[1]
    new_filename = f'thumbnail{ext}'
    
    return os.path.join(video_folder, new_filename)
