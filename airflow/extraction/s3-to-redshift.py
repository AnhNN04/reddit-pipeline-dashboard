# Library import
import psycopg2
from valid import log_progress
from psycopg2 import sql
from valid import log_progress, get_file_name

"""Script will load data into temporary table in Redshift, delete 
records with the same post ID from main table, then insert these from temp table (along with new data) 
to main table."""

# Store our configuration variables
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

f_name= get_file_name()
file_path = f"s3://{BUCKET_NAME}/data/tmp/{f_name}.csv"


# Create Redshift table if it doesn't exist
sql_create_table = sql.SQL(
    """CREATE TABLE IF NOT EXISTS {table} (
                            id varchar PRIMARY KEY,
                            title varchar(max),
                            num_comments int,
                            score int,
                            author varchar(max),
                            created_utc timestamp,
                            url varchar(max),
                            upvote_ratio float,
                            over_18 bool,
                            edited bool,
                            spoiler bool,
                            stickied bool
                        );"""
).format(table=sql.Identifier(TABLENAME))

# Improve process. Creating a temp table may be unnecessary 
# If ID already exists in table, we remove it and add new ID record during load.
create_temp_table = sql.SQL(
    "CREATE TEMP TABLE staging_table (LIKE {table});"
).format(table=sql.Identifier(TABLENAME))

# Copy data from S3 to temp table
sql_copy_to_temp = f"COPY staging_table FROM '{file_path}' iam_role '{REDSHIFT_ROLE}' IGNOREHEADER 1 DELIMITER ',' CSV;"

# Delete some duplicate tuples in final_posts table
delete_from_table = sql.SQL(
    "DELETE FROM {table} USING staging_table WHERE {table}.id = staging_table.id;"
).format(table=sql.Identifier(TABLENAME))

# Insert and Update tupls in final_posts table
insert_into_table = sql.SQL(
    "INSERT INTO {table} SELECT * FROM staging_table;"
).format(table=sql.Identifier(TABLENAME))

# Drop temp table for free up memory
drop_temp_table = "DROP TABLE staging_table;"

# Improve error handling
def connect_to_redshift():
    """Connect to Redshift instance"""
    try:
        rs_conn = psycopg2.connect(
            dbname=DBNAME, user=USERNAME, password=PASSWORD, host=HOST, port=PORT
        )
        # write to log
        log_progress("Step1: Connect to Redshift instance.Successfully!")
        return rs_conn
    except Exception as e:
        # write to log
        log_progress(f"Step1: Unable to connect to Redshift. Error {e}")
        print(f"Unable to connect to Redshift. Error {e}")


def load_data_into_redshift(rs_conn):
    """Load data from S3 into Redshift"""
    with rs_conn:

        cur = rs_conn.cursor()
        cur.execute("SET search_path TO {};".format(SCHEMA))
        cur.execute(sql_create_table)
        cur.execute(create_temp_table)
        cur.execute(sql_copy_to_temp)
        cur.execute(delete_from_table)
        cur.execute(insert_into_table)
        cur.execute(drop_temp_table)
        # write to log
        log_progress("Step2: Load data from S3 into Redshift.Successfully!")
        # Commit only at the end and end up with a temp table and deleted main table if something fails
        rs_conn.commit()

def main():
    """Upload file form S3 to Redshift Table"""
    log_progress("START UPLOAD FILE FROM S3 TO REDSHIFT TABLE:")
    rs_conn = connect_to_redshift()
    load_data_into_redshift(rs_conn)
    log_progress("END UPLOAD FILE FROM S3 TO REDSHIFT TABLE.\n")
    print("Copy from S3 to Redshift Process Finished.")


if __name__ == "__main__":
    main()