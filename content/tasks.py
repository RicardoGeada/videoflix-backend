import subprocess
import os

def convert_480p(source):
    file_name, _ = os.path.splitext(source)
    target = file_name + '_480p.mp4'
    cmd = f'ffmpeg -i "{source}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    subprocess.run(cmd, shell=True)
    return target

def convert_720p(source):
    file_name, _ = os.path.splitext(source)
    target = file_name + '_720p.mp4'
    cmd = f'ffmpeg -i "{source}" -s hd720 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    subprocess.run(cmd, shell=True)
    return target

def convert_1080p(source):
    file_name, _ = os.path.splitext(source)
    target = file_name + '_1080p.mp4'
    cmd = f'ffmpeg -i "{source}" -s hd1080 -c:v libx264 -crf 23 -c:a aac -strict -2 "{target}"'
    subprocess.run(cmd, shell=True)
    return target
    
    
def convert_to_hls(source):
    file_name, _ = os.path.splitext(source)
    hls_target = file_name + '.m3u8'
    cmd = f'ffmpeg -i "{source}" -codec: copy -start_number 0 -hls_time 10 -hls_list_size 0 -f hls "{hls_target}"'
    subprocess.run(cmd, shell=True)
    return hls_target
    
    
def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)