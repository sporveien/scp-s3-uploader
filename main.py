import logging
import os
from datetime import datetime
import yaml
from boto import get_bucket, session, upload_to_bucket
from utils import ping, req  # , trace_route
from logger import logger
from files import move_files, remove_archive


def main():
    try:
        # .yml files
        try:
            # Read .yml config file
            with open("config.yml", 'r', encoding='utf8') as stream:
                conf = yaml.safe_load(stream)
            # Read .yml secrets file
            with open("secrets.yml", 'r', encoding='utf8') as stream:
                secrets = yaml.safe_load(stream)
        except Exception as err_yml:
            log_err = str(".yml exception: {0}").format(err_yml)
            print(log_err)
            raise log_err

        # Set environment variables from config file
        os.environ["AWS_ACCESS_KEY_ID"] = secrets['AWS_ACCESS_KEY']
        os.environ["AWS_SECRET_ACCESS_KEY"] = secrets['AWS_SECRET_KEY']

        # Start logger
        logger(conf['MAX_LOGFILES'], secrets['LOG_ROOT'],
               conf['LOG_FILE_EXTENTSION'], conf['LOG_DATE_TIME_FORMAT'])

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

        # S3 Connection tests
        if conf["S3_CONNECTION_TEST"]:
            # Bucket fqdn
            bucket_fqdn = bucket_name + '.s3.amazonaws.com'
            logging.debug(
                "Ping url '%s'", bucket_fqdn)
            # Ping
            if not ping(bucket_fqdn):
                logging.warning("'%s' is not responding to ping", bucket_fqdn)
            else:
                logging.info(
                    "'%s' is responding to ping function", bucket_fqdn)

            # Get request
            bucket_url = 'https://' + bucket_fqdn
            if not req(bucket_url):
                logging.warning(
                    "'%s' does not return status code 200 or 403", bucket_url)
            else:
                logging.info(
                    "GET request returned expected status code from url '%s'", bucket_url)

            ###############  ?  COULD NEED ELEVATION ? #################
            # Route tracing
            # trace_route_to = str(bucket) + ".s3.amazonaws.com"
            # logging.debug("Trace route to '%s'", trace_route_to)
            # route_trace_result = str(trace_route(trace_route_to))
            # logging.debug(route_trace_result)
            ############################################################

        # Take No Action
        if conf["TAKE_NO_ACTION"]:
            log_msg = str(
                "Take no action is turned on in .yml config")
            logging.info(log_msg)
            return

        # Move files to temp folder to make sure files are not locked. E.g. being written to by another user / job
        move_from_path = str(secrets["DATA_ROOT"])
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

        # Upload to s3 bucket.. Files should now have been moved to the temp storage root path
        upload_result = upload_to_bucket(
            moved_files, bucket, secrets['S3_KEY'])

        log_msg = str("Uploaded a total of {0} file(s) to s3 {1}").format(
            str(len(upload_result)), bucket_name)
        logging.info(log_msg)

        if len(upload_result) < 1:
            log_err = str("No files were uploaded").format(
                move_to_path)
            logging.error(log_err)
            uploaded_all_files = False

        if len(upload_result) < len(moved_files) and len(upload_result) >= 1:
            log_warning = str("Missing filesSome files were {0}").format(
                move_to_path)
            logging.warning(log_warning)
            uploaded_all_files = False

        if len(upload_result) == len(moved_files):
            log_msg = str("Uploaded all files moved to {0}").format(
                move_to_path)
            logging.info(log_msg)
            uploaded_all_files = True

        if not uploaded_all_files and conf["ONLY_ARCHIVE_ON_COMPLETE_UPLOAD"]:
            log_warning = str(
                "Skipping archive management on an uncomplete upload. Archive management is set to only run on fully completed uploads in .yml config.")
            logging.warning(log_warning)
            return

        # Archiving
        if not conf["ARCHIVE_FILES"]:
            log_msg = str(
                "Archiving is turned off in .yml config file")
            logging.info(log_msg)
            return

        # Move files from temp root folder path
        archive_root_path = secrets["ARCHIVE_ROOT"]
        archive_file_timestamp_format = conf["ARCHIVE_FILE_TIMESTAMP_FORMAT"]
        archive_file_prefix = conf["ARCHIVE_FILE_PREFIX"]
        archive_file_suffix = conf["ARCHIVE_FILE_SUFFIX"]
        archive_container_timestamp_format = conf["ARCHIVE_CONTAINER_TIMESTAMP_FORMAT"]
        archive_container_prefix = conf["ARCHIVE_CONTAINER_PREFIX"]
        archive_container_suffix = conf["ARCHIVE_CONTAINER_SUFFIX"]

        # Archive container
        if conf["ARCHIVE_CONTAINER"]:
            archive_stamp = datetime.now().strftime(
                archive_container_timestamp_format)

            archive_container = str("{0}{1}{2}").format(
                archive_container_prefix, archive_stamp, archive_container_suffix)

            archive_container = archive_container.replace(" ", "")

            to_archive_path = os.path.join(
                archive_root_path, archive_container)
        else:
            to_archive_path = archive_root_path

        log_msg = str("Archive file(s) from archive temp root path {0} to archive root path {1}").format(
            move_to_path, to_archive_path)
        logging.info(log_msg)

        archived_files = move_files(
            move_to_path, to_archive_path)

        log_msg = str("Archived a total of {0} file(s)").format(
            str(len(archived_files)))
        logging.info(log_msg)

        # Clean up the archive
        if not conf["CLEAN_UP_ARCHIVE"]:
            log_msg = str(
                "Clean up archive is turned off in .yml config file")
            logging.info(log_msg)
            return

        archive_retention_time = conf["ARCHIVE_RETENTION_TIME_HOURS"]

        log_msg = str("Clean up archives in archive root path {0}").format(
            archive_root_path)
        logging.info(log_msg)

        if conf["ARCHIVE_CONTAINER"]:
            cleaup_up_result = remove_archive(archive_retention_time, archive_root_path, archive_container_prefix,
                                              archive_container_suffix, archive_container_timestamp_format, True)
        else:
            cleaup_up_result = remove_archive(archive_retention_time, archive_root_path, archive_file_prefix,
                                              archive_file_suffix, archive_file_timestamp_format, False)

        log_msg = str("Clean up archive result {0}").format(cleaup_up_result)
        logging.info(log_msg)

    # Main error handler
    except Exception as err_main:
        logging.error('Main exception: %s', str(err_main))
        raise


if __name__ == '__main__':
    main()
