import subprocess
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Import all data (videos, genres, and users) using their respective commands.'

    def handle(self, *args, **kwargs):
        try:
            # import_videos
            subprocess.call(['python', 'manage.py', 'import_videos'], shell=True)
            self.stdout.write(self.style.SUCCESS('Videos import successful.'))

            # import_genres
            subprocess.call(['python', 'manage.py', 'import_genres'], shell=True)
            self.stdout.write(self.style.SUCCESS('Genres import successful.'))

            # import_users
            subprocess.call(['python', 'manage.py', 'import_users'], shell=True)
            self.stdout.write(self.style.SUCCESS('Users import successful.'))

            self.stdout.write(self.style.SUCCESS('All imports completed successfully.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during import: {e}'))
