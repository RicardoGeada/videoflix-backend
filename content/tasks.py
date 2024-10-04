import subprocess
import os

def convert_to_hls(source, resolution):

    allowed_resolutions = ['480', '720', '1080']
    if resolution not in allowed_resolutions:
        raise ValueError(f"Invalid resolution. Please choose from {allowed_resolutions}")  
    
    file_name, _ = os.path.splitext(source)
    hls_target = file_name + f'_{resolution}p.m3u8'
    cmd = (
        f'ffmpeg -i "{source}" -s hd{resolution} -c:v libx264 -crf 23 -c:a aac '
        f'-start_number 0 -hls_time 10 -hls_list_size 0 -f hls "{hls_target}"'
    )
    
    subprocess.run(cmd, shell=True)
    return hls_target
    
    
def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        

