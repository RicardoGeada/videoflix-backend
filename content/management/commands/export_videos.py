import os
from django.core.management.base import BaseCommand
from content.admin import VideoResource

class Command(BaseCommand):
    help = 'Export data to a JSON file.'
    
    def handle(self, *args, **kwargs):
       export_videos(self) 

def export_videos(self):
    os.makedirs('data', exist_ok=True)
    dataset = VideoResource().export()
    file_path = os.path.join('data', 'data_videos.json')
    with open(file_path, 'w') as file:
        file.write(dataset.json)
        
    self.stdout.write(self.style.SUCCESS(f'Data successfully exported to {file_path}'))