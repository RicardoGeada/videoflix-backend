import os
from django.core.management.base import BaseCommand
from content.admin import GenreResource

class Command(BaseCommand):
    help = 'Export data to a JSON file.'
    
    def handle(self, *args, **kwargs):
       export_genres(self) 

def export_genres(self):
    os.makedirs('data', exist_ok=True)
    dataset = GenreResource().export()
    file_path = os.path.join('data', 'data_genres.json')
    with open(file_path, 'w') as file:
        file.write(dataset.json)
        
    self.stdout.write(self.style.SUCCESS(f'Data successfully exported to {file_path}'))