
def video_upload_path(instance, filename):
    """
    Generates a file path for uploaded video files.
    The path includes the ID of the instance to ensure unique storage directories.
    """
    return f'videos/{instance.pk}/{filename}'
