import os
from django.core.management.base import BaseCommand
from users.admin import UsersResource 
from tablib import Dataset 

class Command(BaseCommand):
    help = 'Import data from a JSON file.'

    def handle(self, *args, **kwargs):
        
        file_path = os.path.join('data', 'data_users.json')
        
        # Check if the file exists
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File {file_path} does not exist.'))
            return
        
        # Open the file and read its content
        with open(file_path, 'r') as file:
            json_data = file.read()
        
        video_resource = UsersResource()

        # Create a Dataset object and load the JSON data
        dataset = Dataset().load(json_data, format='json')

        # Import the data
        result = video_resource.import_data(dataset, raise_errors=True)
        
        # Provide feedbak in terminal
        self.stdout.write(self.style.SUCCESS('Data successfully imported from JSON file.'))
