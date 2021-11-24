from os import path
import logging
import boto3
from botocore.exceptions import ClientError


def session(aws_access_key_id, aws_secret_access_key):
    try:
        boto_session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        if boto_session:
            return boto_session
    except Exception as err_session:
        raise err_session


# def getAllBuckets():
#     try:
#         response = s3.list_buckets()
#         logging.info(str(response))
#         buckets = response['Buckets']
#         logging.info("Successfully found a total of " +
#                      str(len(buckets)) + " s3 buckets")
#         return buckets
#     except Exception as E:
#         raise


def get_bucket(boto_session, s3_bucket):
    try:
        s3 = boto_session.resource('s3')
        bucket = s3.Bucket(s3_bucket)
        return bucket
    except Exception as err_get_bucket:
        raise err_get_bucket


def upload_to_bucket(files, s3_bucket, object_name):
    files_uploaded = []
    for file in files:
        if object_name is None:
            s3_key = path.basename(file).replace(
                "/", "").replace("\\", "")
        else:
            file_base_name = str(path.basename(
                file).replace("/", "").replace("\\", ""))
            s3_key = str(object_name + "/" + file_base_name)

        try:
            bucket_name = s3_bucket.name

            response = s3_bucket.put_object(
                Body=file, Bucket=bucket_name, Key=s3_key)

            files_uploaded.append(file)

            log_msg = str("Successfully uploaded {0} to s3 bucket {1} as {2}").format(
                file, bucket_name, s3_key)
            logging.info(log_msg)
            log_msg = str("Boto response: {0}").format(response)
            logging.debug(log_msg)

            file_base_name = None
        except ClientError as err:
            err_msg = str("Failed to upload {0} to s3 bucket {1} key {2}. Boto client error: {3}").format(
                file, s3_bucket, s3_key, err)
            logging.error(err_msg)
        s3_key = ''
    return files_uploaded
