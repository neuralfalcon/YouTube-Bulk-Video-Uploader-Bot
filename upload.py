from selenium import webdriver
import time
import os
import json
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import glob
import re
# Load configuration from a JSON file
with open("paths.json", "r") as json_file:
    data = json.load(json_file)

executable_path = data["Executable Path"]
profile_path = data["Profile Path"]
videos_path = data["Videos Path"]
internet_speed = data["Internet Speed"]

# Configure Chrome options with user data directory and binary location
options = webdriver.ChromeOptions()
options.add_argument("--log-level=3")
options.add_argument(f"user-data-dir={profile_path}")
options.binary_location = executable_path
options.add_argument("--disable-blink-features=AutomationControlled")

def calculate_upload_waiting_time(file_path, internet_speed_mbps):
    # Get the size of the video file in bits (1 byte = 8 bits)
    file_size_bits = os.path.getsize(file_path) * 8  # Get file size in bits
    file_size_mb = file_size_bits / (1024 ** 2)  # Convert to megabits
    waiting_time_seconds = file_size_mb / internet_speed_mbps
    return waiting_time_seconds + 10

def compare_dates(input_date):
    current_time = datetime.datetime.now()
    try:
        input_datetime = datetime.datetime.strptime(input_date, "%d/%m/%Y, %H:%M")
        if input_datetime >= current_time:
            return input_datetime.strftime("%d/%m/%Y, %H:%M")
        else:
            current_time += datetime.timedelta(hours=2)
            return current_time.strftime("%d/%m/%Y, %H:%M")
    except Exception as e:
        current_time += datetime.timedelta(hours=2)
        return current_time.strftime("%d/%m/%Y, %H:%M")

def convert_date_format(input_date):
    input_datetime = datetime.datetime.strptime(input_date, "%d/%m/%Y, %H:%M")
    formatted_date = input_datetime.strftime("%b %d, %Y")
    formatted_time = input_datetime.strftime("%H:%M")
    return formatted_date, formatted_time

def upload_youtube_video(movie_path, json_file_path, img_path):
    global internet_speed
    time.sleep(1)

    upload_button = bot.find_element(By.XPATH, '//*[@id="upload-icon"]')
    upload_button.click()
    time.sleep(1)

    # Specify the path to the video file
    video_path = os.path.abspath(movie_path)

    # Locate the file input element and upload the video
    file_input = bot.find_element(By.XPATH, '//*[@id="content"]/input')
    file_input.send_keys(video_path)
    time.sleep(calculate_upload_waiting_time(video_path, internet_speed))  # Adjust the timeout as needed based on file size
    
    if os.path.exists(img_path):
        thumbnail_path = os.path.abspath(img_path)
        print(thumbnail_path)
        thumbnail_input = bot.find_element(By.XPATH, "//input[@id='file-loader']")
        thumbnail_input.send_keys(thumbnail_path)
    else:
        print(img_path)
    time.sleep(1)

    title, tags, description, schedule = read_json_file(json_file_path)

    title_input = bot.find_element(By.ID, 'textbox')
    title_input.clear()
    title_input.send_keys(title)

    textboxes = bot.find_elements(By.ID, 'textbox')

    if len(description) > 1:
        description_element = textboxes[1]
        description_element.clear()
        encoded_description = description.encode('utf-8')
        description_element.send_keys(encoded_description.decode('utf-8'))

    if len(tags) > 1:
        enable_tags_button = bot.find_element(By.XPATH, '//*[@id="toggle-button"]/div')
        enable_tags_button.click()
        wait = WebDriverWait(bot, 10)
        tags_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="text-input"]')))
        tags_input.clear()
        tags_input.send_keys(tags)

    next_button = bot.find_element(By.XPATH, '//*[@id="next-button"]')
    for i in range(3):
        next_button.click()
        time.sleep(1)
    time.sleep(2)

    SCHEDULE_CONTAINER_ID = 'schedule-radio-button'
    SCHEDULE_DATE_ID = 'datepicker-trigger'
    SCHEDULE_DATE_TEXTBOX = '/html/body/ytcp-date-picker/tp-yt-paper-dialog/div/form/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input'
    SCHEDULE_TIME = "/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[3]/ytcp-visibility-scheduler/div[1]/ytcp-datetime-picker/div/div[2]/form/ytcp-form-input-container/div[1]/div/tp-yt-paper-input/tp-yt-paper-input-container/div[2]/div/iron-input/input"

    if schedule:
        formatted_date, formatted_time = convert_date_format(schedule)
        wait = WebDriverWait(bot, 10)
        schedule_button = wait.until(EC.element_to_be_clickable((By.ID, SCHEDULE_CONTAINER_ID)))
        schedule_button.click()
        bot.find_element(By.ID, SCHEDULE_DATE_ID).click()
        bot.find_element(By.XPATH, SCHEDULE_DATE_TEXTBOX).clear()
        bot.find_element(By.XPATH, SCHEDULE_DATE_TEXTBOX).send_keys(formatted_date)
        bot.find_element(By.XPATH, SCHEDULE_DATE_TEXTBOX).send_keys(Keys.ENTER)
        time.sleep(1)
        bot.find_element(By.XPATH, SCHEDULE_TIME).click()
        bot.find_element(By.XPATH, SCHEDULE_TIME).clear()
        bot.find_element(By.XPATH, SCHEDULE_TIME).send_keys(formatted_time)
        bot.find_element(By.XPATH, SCHEDULE_TIME).send_keys(Keys.ENTER)
        print(f"Scheduled the video for {formatted_date} {formatted_time}")
    else:
        public_main_button = bot.find_element(By.NAME, 'PUBLIC')
        bot.find_element(By.ID, 'radioLabel', public_main_button).click()

    time.sleep(2)
    done_button = bot.find_element(By.XPATH, '//*[@id="done-button"]')
    done_button.click()
    last_wating=calculate_upload_waiting_time(video_path, internet_speed)
    if last_wating>40:
        time.sleep(15)
    else:
        time.sleep(10)
    close_button = bot.find_element(By.XPATH, '//*[@id="close-button"]/div')
    close_button.click()

def read_json_file(file_path):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    youtube_title = data["youtube_title"]
    tags = data["tags"]
    total_length = sum(len(tag) for tag in tags)
    
    while total_length > 480 and len(tags) > 0:
        removed_tag = tags.pop()
        total_length -= len(removed_tag)
    tags_sentence = ", ".join(tags)
    description = data["description"]
    schedule = data["schedule"]
    schedule = compare_dates(schedule)
    return youtube_title, tags_sentence, description, schedule

def preprocess_title(title):
    processed_title = re.sub(r'[^\w\s]', '', title).replace(' ', '').lower()
    return processed_title

bot = webdriver.Chrome(options=options)
url = "https://studio.youtube.com"
bot.get(url)
youtube_thumbnail_extensions=[".png",".jpg",".jpeg"]
upload_success_files=[]
upload_fail_files=[]
for i in glob.glob(f"{videos_path}/*.mp4"):
    i = i.replace("\\", "/")
    video_path = i
    title = i.split("/")[-1]
    title = title.replace(".mp4", "")
    json_file_path = i.replace(".mp4", ".json")
    image_base_path = video_path.split(".mp4")[0]

    for ext in youtube_thumbnail_extensions:
        thumbnail_path = f"{image_base_path}{ext}"
        print("before "+thumbnail_path)
        if os.path.exists(thumbnail_path):
            print(f"Thumbnail found: {thumbnail_path}")
            break
    else:
        thumbnail_path = f"{image_base_path}.png"
    
    try:
        upload_youtube_video(video_path, json_file_path, thumbnail_path)
        upload_success_files.append(video_path)
    except Exception as e:
        upload_fail_files.append(video_path)
        print(e)
        bot.quit()
        bot = webdriver.Chrome(options=options)
        url = "https://studio.youtube.com"
        bot.get(url)

file_name = "upload_success.txt"

# Open the file in write mode and write the filenames to it
with open(file_name, "w") as file1:
    for filename in upload_success_files:
        file1.write(filename + "\n")
        
file_name = "upload_fail.txt"

# Open the file in write mode and write the filenames to it
with open(file_name, "w") as file2:
    for filename in upload_fail_files:
        file2.write(filename + "\n")        
bot.quit()
