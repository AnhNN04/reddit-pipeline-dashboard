
# Import libs
from datetime import datetime, timedelta
import datetime
import pandas as pd
import pathlib
import praw
import sys
import numpy as np
from valid import log_progress, file_name, get_file_name


# This is a part from DAG. Taking in one command line argument of format YYYYMMDD.
# Script will connect to REddit API and extract top posts from past day with no limits.
# For a small subreddit like Data Engineering, this should extract all posts from the past 24 hours

# Configuration Variables
with open('./env-config.conf','r') as file:
    lines = file.readlines()
    CLIENT_ID = lines[1].strip().split(" ")[1]
    SECRET_KEY = lines[2].strip().split(" ")[1]
    DEVELOPER = lines[3].strip().split(" ")[1]
    SUBREDDIT = lines[4].strip().split(" ")[1]
    TIME_FILTER = lines[5].strip().split(" ")[1]
    LIMIT = lines[6].strip().split(" ")[1]
    USER_AGENT = lines[7].strip().split(" ")[1]
    PASSWORD = lines[8].strip().split(" ")[1]


# Fields that will be extracted from Reddit.
# Check PRAW documentation for additional fields. if you change these, you'll need to update the create table sql query in the upload_aws_redshift.py file

POST_FIELDS = (
    "id",
    "title",
    "score",
    "num_comments",
    "author",
    "created_utc",
    "url",
    "upvote_ratio",
    "over_18",
    "edited",
    "spoiler",
    "stickied",
)

# Improve error handling
def api_connect():
    """Connect to Reddit API"""
    try:
        reddit_instance = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=SECRET_KEY,
            user_agent=USER_AGENT,
            username=DEVELOPER,
            password=PASSWORD
        )
        # write to log file
        log_progress(f"Step1: Connect to Reddit API. Successfully!")
        return reddit_instance
    except Exception as e:
        print(f"Unable to connect to API. Error: {e}")
        # write to log file
        log_progress(f"Step1: Unable to connect to API. Error: {e}")
        sys.exit(1)


# Improve error handling
def subreddit_posts(reddit_instance):
    """Create posts object for Reddit instance"""
    try:
        subreddit = reddit_instance.subreddit(SUBREDDIT)
        posts = subreddit.top(time_filter=TIME_FILTER, limit=int(LIMIT)) # LIMIT here
        # write to log file
        log_progress(f"Step2: Create posts object for Reddit instance. Successfully!")
        return posts
    except Exception as e:
        print(f"There's been an issue. Error: {e}")
        # write to log file
        log_progress(f"Step2: There's been an issue with subreddit. Error: {e}")
        sys.exit(1)

# Improve error handling
def extract_data(posts):
    """Extract Data to Pandas DataFrame object"""
    items_list = []
    try:
        for post in posts:
            # initialize a dict for each post
            post_data = {}
            for field in POST_FIELDS:
                value = getattr(post,field,None)
                post_data[field] = value
            # append post_dict to list of post
            items_list.append(post_data)
        # convert list_of_dict to dataframe
        extracted_data_df = pd.DataFrame(items_list)
        # write to log file
        log_progress("Step3: Extract Data to Pandas DataFrame object. Successfully!")
        return extracted_data_df
    except Exception as e:
        print(f"There has been an issue. Error {e}")
        # write to log file
        log_progress(f"Step3: There has been an issue. Error {e}")
        sys.exit(1)


 # Remove all but the edited line, as not necessary. 
 # For edited line, rather than force as boolean, keep date-time of last edit and set all else to None.
def transform_basic(df):
    """Some basic transformation of data. To be refactored at a later point."""
    # Convert epoch to UTC
    df["created_utc"] = pd.to_datetime(df["created_utc"], unit="s")
    # Fields don't appear to return as booleans (e.g. False or Epoch time). Needs further investigation but forcing as False or True for now.
    df["over_18"] = np.where(
        (df["over_18"] == "False") | (df["over_18"] == False), False, True
    ).astype(bool)
    df["edited"] = np.where(
        (df["edited"] == "False") | (df["edited"] == False), False, True
    ).astype(bool)
    df["spoiler"] = np.where(
        (df["spoiler"] == "False") | (df["spoiler"] == False), False, True
    ).astype(bool)
    df["stickied"] = np.where(
        (df["stickied"] == "False") | (df["stickied"] == False), False, True
    ).astype(bool)
    # write to log file
    log_progress("Step4: Some basic transformation of data. Successfully!")
    return df


def load_to_csv(extracted_data_df):
    """Save extracted data to CSV file in /data folder"""
    file_name()
    f_name = get_file_name()
    extracted_data_df.to_csv(f"./data/tmp/{f_name}.csv", index=False)
    # write to log file
    log_progress("Step5: Save extracted data to CSV file in /data/tmp folder. Successfully!")

def main():
    """Extract Reddit data and load to CSV"""
    # write to log file
    log_progress("START REDDIT-API PROCESSING")
    reddit_instance = api_connect()
    subreddit_posts_object = subreddit_posts(reddit_instance)
    extracted_data = extract_data(subreddit_posts_object)
    transformed_data = transform_basic(extracted_data)
    load_to_csv(transformed_data)
    # write to log file
    log_progress("END REDDIT-API PROCESSING\n")
    print("Reddit Extract Processes Finished.")


if __name__ == "__main__":
    main()