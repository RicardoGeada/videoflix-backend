import subprocess
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Export all data (videos, genres, and users) using their respective commands.'

    def handle(self, *args, **kwargs):
        try:
            # export_videos
            subprocess.call(['python', 'manage.py', 'export_videos'], shell=True)
            self.stdout.write(self.style.SUCCESS('Videos export successful.'))

            # export_genres 
            subprocess.call(['python', 'manage.py', 'export_genres'], shell=True)
            self.stdout.write(self.style.SUCCESS('Genres export successful.'))

            # export_users
            subprocess.call(['python', 'manage.py', 'export_users'], shell=True)
            self.stdout.write(self.style.SUCCESS('Users export successful.'))

            self.stdout.write(self.style.SUCCESS('All exports completed successfully.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during export: {e}'))
