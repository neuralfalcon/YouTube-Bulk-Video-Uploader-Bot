import glob
import datetime
import re 
import os 
import json 
import speedtest

speed_test = speedtest.Speedtest()
def get_speed():
  download_speed = speed_test.upload()
  KB = 1024 # One Kilobyte is 1024 bytes
  MB = KB * 1024 # One MB is 1024 KB
  speed=int(download_speed/MB)/8
  return speed


executable_path = r"C:\Program Files\Google\Chrome Beta\Application\chrome.exe"
profile_path = r"C:\Users\flacon\AppData\Local\Google\Chrome Beta\User Data\Default"
videos_folder_path = r"C:\Users\falcon\Desktop\videos"

i_known_my_internet_speed=41.37
internet_speed=(i_known_my_internet_speed/8)  
#or
# internet_speed=get_speed() #i don't know my internet speed




def get_current_time():
    current_time = datetime.datetime.now()
    current_time = current_time + datetime.timedelta(minutes=15)
    new_time = current_time.strftime("%d/%m/%Y, %H:%M")
    return new_time

def sanitize_filename(filename):
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    sanitized = sanitized.replace(".", " ")
    sanitized = sanitized.strip()
    return sanitized

def blank_json(save_path, title):
    json_file_name = f"{save_path}/{sanitize_filename(title)}.json"
    youtube_title = title
    description = ""
    tags = []
    schedule = get_current_time()
    data = {
        "youtube_title": youtube_title,
        "tags": tags,
        "description": description,
        "schedule": schedule,
    }
    with open(json_file_name, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def generate_jasons(your_path):
    for i in glob.glob(f"{your_path}/*.mp4"):
        i = i.replace("\\", "/")
        video_path = i
        title = i.split("/")[-1]
        title = title.replace(".mp4", "")
        json_file_path = i.replace(".mp4", ".json")
        thumbnail_path = i.replace(".mp4", ".png")
        if not os.path.exists(json_file_path):
            blank_json(your_path, title)
        if not os.path.exists(thumbnail_path):
            thumbnail_path = None
        print(video_path)
        print(json_file_path)
        print(thumbnail_path)
        print("\n")
        


def convert_and_save_paths(executable_path, profile_path, videos_folder_path,internet_speed):
    profile_path = profile_path.replace("Default", "")
    converted_executable_path = executable_path.replace("\\", "\\\\")
    converted_profile_path = profile_path.replace("\\", "\\\\")
    speed = internet_speed
    data = {
        "Executable Path": converted_executable_path,
        "Profile Path": converted_profile_path,
        "Videos Path": videos_folder_path,
        "Internet Speed": speed
    }
    with open("paths.json", "w") as json_file:
        json.dump(data, json_file,indent=4)
    generate_jasons(videos_folder_path)
    return "Paths converted and saved as 'paths.json' & blank json created"

# internet_speed=5
convert_and_save_paths(executable_path, profile_path, videos_folder_path,internet_speed)
