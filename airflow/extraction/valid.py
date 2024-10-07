import sys
from datetime import datetime
# Log functions for record time and message for all details during this process.
def log_progress(message):
    time_format = '%Y-%m-%d %H:%M:%S'
    now = datetime.now()
    time_strftime = now.strftime(time_format)
    with open("./data/logs.txt",'a') as f:
        write_format = f"{time_strftime}: {message}\n"
        f.write(write_format)

def file_name():
    time_format = '%Y-%m-%d-%H-%M-%S'
    now = datetime.now()
    time_strftime = now.strftime(time_format)
    with open('./data/file_name.txt','a') as file:
        file.write(str(time_strftime + '\n'))

def get_file_name():
  with open('./data/file_name.txt','r') as file:
      lines = file.readlines()
      return lines[-1].strip()

