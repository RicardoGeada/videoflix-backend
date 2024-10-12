from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible



def validate_jpeg_file(value):
    if not value.name.lower().endswith('.jpeg') and not value.name.lower().endswith('.jpg'):
        raise ValidationError('The image must be in JPEG format.')
    
    
    
@deconstructible
class ValidateFileSize:
    def __init__(self, max_size_mb):
        self.max_size_mb = max_size_mb

    def __call__(self, value):
        max_size = self.max_size_mb * 1024 * 1024
        if value.size > max_size:
            raise ValidationError(f'Max file size {self.max_size_mb} MB allowed.')