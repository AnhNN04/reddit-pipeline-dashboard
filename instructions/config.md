
# Configuration

Next, you'll need to create a configuration file with your details. The extract and load scripts in our pipeline will utilise the details here.

## Setup

1. Create a configuration file under `~/REDDIT-PIPELINE-DASHBOARD/` called `env-config.conf`:

    ```bash
    touch ~/REDDIT-PIPELINE-DASHBOARD/configuration.conf
    ```

1. Copy in the following:

    ```conf
    For RedditAPI:
    --CLIENT_ID= XXXX
    --SECRET_KEY= XXXX
    --DEVELOPER= XXXX
    ...

    For AWS Services:
    -root-user:
    --ALIAS= XXXX
    --ROOT_ID= XXXX
    --IAM_USER_NAME= XXXX
    --PASSWORD= XXXX

    -s3 bucket:
    --ACCESS_KEY= XXXX
    --SECRET_ACCESS_KEY= XXXX
    --AWS_REGION= XXXX
    --BUCKET_NAME= XXXX
    --SERVICE_NAME= XXXX
    ...

    -redshift:
    --HOST= XXXX
    --PORT= XXXX
    --USERNAME= XXXX
    --PASSWORD= XXXX
    ...
    ```


1. Change `XXXXX` values

    * If you need a reminder of your `aws_config` details, change folder back into the terraform folder and run the command. It will output the values you need to store under `aws_config`. Just be sure to remove any `"` from the strings.

        ```bash
        terraform output
        ```
        
    * For `reddit_config` these are the details you took note of after setting up your Reddit App. Note the `developer` is your Reddit name.

---

[Previous Step](setup_infrastructure.md) | [Next Step](docker-airflow.md)

or

[Back to main README](../README.md)
