import logging
import os
import yaml
from boto import get_bucket, session, upload_to_bucket
from utils import ping, req  # , trace_route
from logger import logger
from files import move_files, remove_archive  # , get_files


def main():
    try:
        # .yml files
        try:
            # Read .yml Config file
            with open("config.yml", 'r', encoding='utf8') as stream:
                conf = yaml.safe_load(stream)
            # Read .yml Creds file
            with open("secrets.yml", 'r', encoding='utf8') as stream:
                secrets = yaml.safe_load(stream)
        except Exception as err_yml:
            print(err_yml)
            raise err_yml

        # Set environment variables from config file
        os.environ["AWS_ACCESS_KEY_ID"] = secrets['AWS_ACCESS_KEY']
        os.environ["AWS_SECRET_ACCESS_KEY"] = secrets['AWS_SECRET_KEY']

        # Start logger
        logger(conf['MAX_LOGFILES'], secrets['LOG_ROOT'])

        # Boto session
        logging.debug(
            "Starting Boto session")
        botosession = session(os.environ["AWS_ACCESS_KEY_ID"],
                              os.environ["AWS_SECRET_ACCESS_KEY"])
        logging.debug(
            "Boto session successfully started")

        # Get s3 bucket
        logging.debug(
            "Getting bucket '%s'", secrets['S3_BUCKET'])
        bucket = get_bucket(botosession, secrets['S3_BUCKET'])
        bucket_name = bucket.name
        logging.debug(
            "Successfully got s3 bucket '%s'", bucket_name)
        # Bucket https url
        bucket_url = 'https://' + bucket_name + '.s3.amazonaws.com'
        logging.debug(
            "Ping url '%s'", bucket_url)

        # Ping
        if not ping(bucket_url):
            logging.warning("'%s' is not responding to ping", bucket_url)
        else:
            logging.info("'%s' is responding to ping function", bucket_url)

        # Get request
        if not req(bucket_url):
            logging.warning(
                "'%s' does not return status code 200 or 403", bucket_url)
        else:
            logging.info(
                "GET request returned expected status code from url '%s'", bucket_url)

        ###############    NEEDS SUDO RIGHTS ####################
        # Route tracing
        # trace_route_to = str(bucket) + ".s3.amazonaws.com"
        # logging.debug("Trace route to '%s'", trace_route_to)
        # route_trace_result = str(trace_route(trace_route_to))
        # logging.debug(route_trace_result)
        #########################################################

        # Move files to temp folder to make sure files are not locked. E.g. being written to by another user / job
        move_from_path = str(secrets["LOCAL_ROOT"])
        move_to_path = str(secrets["TEMP_ROOT"])

        log_msg = str("Move files from {0} to {1}").format(
            move_from_path, move_to_path)
        logging.info(log_msg)

        moved_files = move_files(move_from_path, move_to_path)

        log_msg = str("Moved a total of {0} file(s)").format(
            str(len(moved_files)))
        logging.info(log_msg)

        if len(moved_files) < 1:
            log_warning = str(
                "No files to upload since no file(s) were moved to {0}").format(move_to_path)
            logging.warning(log_warning)
            return

        # Upload to s3 bucket, files should now have been moved to the temp storage path
        upload_result = upload_to_bucket(
            moved_files, bucket, secrets['S3_KEY'])

        log_msg = str("Uploaded a total of {0} file(s) to s3 {1}").format(
            upload_result, bucket_name)
        logging.info(log_msg)

        if upload_result == len(moved_files):
            log_msg = str("Uploaded all files moved to {0}").format(
                move_to_path)
            logging.info(log_msg)
            uploaded_all_files = True

        if upload_result < 1:
            log_err = str("No files were uploaded").format(
                move_to_path)
            logging.error(log_err)
            uploaded_all_files = False

        if upload_result < len(moved_files):
            log_warning = str("Did not upload every file moved to {0}").format(
                move_to_path)
            logging.warning(log_warning)
            uploaded_all_files = False

        if not uploaded_all_files:
            log_warning = str(
                "Archive clean up is skipped becuse one or more files did not get uploaded to S3")
            logging.warning(log_warning)
            return

        # Clean up archive if every file moved to temp folder was uploaded to s3
        archive_retention_time = conf["ARCHIVE_RETENTION_TIME_HOURS"]
        archive_path = os.path.abspath(os.getcwd()) + secrets["ARCHIVE_ROOT"]
        archive_file_prefix = conf["ARCHIVE_FILE_PREFIX"]
        archive_file_ext = conf["ARCHIVE_FILE_EXTENSION"]
        archive_file_timestamp_format = conf["ARCHIVE_FILE_TIMESTAMP_FORMAT"]

        remove_archive(archive_retention_time, archive_path, archive_file_prefix,
                       archive_file_ext, archive_file_timestamp_format)

    # Main error handler
    except Exception as err_main:
        logging.error('Main exception: %s', str(err_main))
        raise


if __name__ == '__main__':
    main()
