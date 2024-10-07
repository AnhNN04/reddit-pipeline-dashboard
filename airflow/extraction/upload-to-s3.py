# Import Libraries
import boto3
import botocore
from valid import log_progress, get_file_name

# Name for S3 file
with open('./env-config.conf','r') as file:
    lines = file.readlines()
    ACCESS_KEY = lines[18].strip().split(" ")[1]
    SECRET_KEY = lines[19].strip().split(" ")[1]
    AWS_REGION = lines[20].strip().split(" ")[1]
    BUCKET_NAME = lines[21].strip().split(" ")[1]
    SERVICE_NAME = lines[22].strip().split(" ")[1]

# Improve error handling
def connect_to_s3():
    """Connect to S3 Instance"""
    try:
        conn = boto3.resource(
            service_name=SERVICE_NAME,
            region_name=AWS_REGION,
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY
            )
        # wrire to log:
        log_progress("Step1: Connect to S3 Instance. Successfully!")
        return conn
    except Exception as e:
        print(f"Can't connect to S3. Error: {e}")
        # wrire to log:
        log_progress(f"Step1: Cant't connect to S3. Error: {e}")

# Improve error handling
def create_bucket_if_not_exists(conn):
    """Check if bucket exists and create if not"""
    log_progress(f"Step2: Check if Bucket exists and create if not. Successfully!")
    exists = True
    try:
        conn.meta.client.head_bucket(Bucket=BUCKET_NAME)
    except botocore.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            exists = False
    if not exists:
        conn.create_bucket(
            Bucket=BUCKET_NAME,
            CreateBucketConfiguration={"LocationConstraint": AWS_REGION}
        )

def upload_file_to_s3(conn):
    """Upload file to S3 Bucket"""
    f_name = f"data/tmp/{get_file_name()}.csv"
    conn.meta.client.upload_file(
        Filename=f_name, Bucket=BUCKET_NAME, Key=f_name
    )
    # wrire to log:
    log_progress("Step3: Unpoad file to S3 bucket.Successfully!")

def main():
    """Upload input file to S3 bucket"""
    # wrire to log:
    log_progress("START S3 BUCKET UPLOADING:")
    conn = connect_to_s3()
    create_bucket_if_not_exists(conn)
    upload_file_to_s3(conn)
    # wrire to log:
    log_progress("END S3 BUCKET UPLOADING.\n")
    print("S3 Bucket Processes Finished.")

if __name__ == "__main__":
    main()