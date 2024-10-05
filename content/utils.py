
def video_upload_path(instance, filename):
    """
    Generates a file path for uploaded video files.
    The path includes the ID of the instance to ensure unique storage directories.
    """
    clean_title = instance.title.replace(' ', '_').lower()
    return f'videos/{instance.pk}_{clean_title}/{filename}'
