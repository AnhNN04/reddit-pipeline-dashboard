from valid import log_progress, get_file_name
import psycopg2
from psycopg2 import sql
import csv
import pandas as pd

"""
Download Redshift table to CSV file. Will be stored under /data folder.
"""

# Store configuration variables
with open('./env-config.conf','r') as file:
    lines = file.readlines()
    HOST= lines[25].strip().split(" ")[1]
    PORT= lines[26].strip().split(" ")[1]
    USERNAME= lines[27].strip().split(" ")[1]
    PASSWORD= lines[28].strip().split(" ")[1]
    DBNAME= lines[29].strip().split(" ")[1]
    SCHEMA= lines[30].strip().split(" ")[1]
    TABLENAME= lines[31].strip().split(" ")[1]
    BUCKET_NAME= lines[21].strip().split(" ")[1]
    ACCOUNT_ID= lines[13].strip().split(" ")[1]
    REDSHIFT_ROLE= lines[32].strip().split(" ")[1]


# Improve error handling
def connect_to_redshift():
    """Connect to Redshift instance"""
    try:
        rs_conn = psycopg2.connect(
            dbname=DBNAME, user=USERNAME, password=PASSWORD, host=HOST, port=PORT
        )
        log_progress("Step1: Connect to Redshift instance.Successfully!")
        return rs_conn
    except Exception as e:
        log_progress(f"Step1: Unable to connect to Redshift. Error {e}")
        print(f"Unable to connect to Redshift. Error {e}")

# Error handling
def download_redshift_data(rs_conn):
    """Download data from Redshift table to CSV"""
    with rs_conn:
        cur = rs_conn.cursor()
        cur.execute("SET search_path TO {};".format(SCHEMA))
        cur.execute(
            sql.SQL("SELECT * FROM {table};").format(table=sql.Identifier(TABLENAME))
        )
        result = cur.fetchall()
        headers = [col[0] for col in cur.description]
        result.insert(0, tuple(headers))
        fp = open("./data/redshift_output.csv", "w")
        myFile = csv.writer(fp)
        myFile.writerows(result)
        fp.close()
    log_progress("Step2: Download data from Redshift table to CSV.Successfully!")

def main():
    #Download Redshift table to CSV file
    log_progress("START DOWNLAOD REDSHIFT TABLE TO CSV FILE:")
    rs_conn = connect_to_redshift()
    download_redshift_data(rs_conn)
    log_progress("END DOWNLOAD REDSHIFT TABLE TO CSV FILE.\n")
    print("Redshift to csv Processes Finished.")

if __name__ == "__main__":
    main()
