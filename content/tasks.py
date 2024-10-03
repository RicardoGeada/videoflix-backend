import subprocess
import os

def convert_480p(source):
    file_name, _ = os.path.splitext(source)
    target = file_name + '_480p.mp4'
    cmd = f'ffmpeg -i "{source}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    subprocess.run(cmd, shell=True)