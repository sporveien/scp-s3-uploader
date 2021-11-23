import os
import logging
import datetime
import glob
from utils import operating_system

LOG_EXTENTSION = '.log'
LOG_DATE_TIME_FORMAT = '%d%m%Y_%H%M%S'


def path(path):
    try:
        if operating_system() == "windows":
            file_path = path + "\\"
        else:
            file_path = path + "/"
        return file_path
    except Exception as err_path:
        raise err_path


def clean_up(max_logfiles, log_root):
    try:
        counter = 0
        log_path = path(log_root)
        files = sorted(glob.glob(log_path + "*" + LOG_EXTENTSION))
        log_msg = str("{0} {1} file(s) in log path {2}").format(
            str(len(files)), LOG_EXTENTSION, log_path)
        logging.info(log_msg)

        if len(files) < max_logfiles:
            log_msg = str("The limit of {0} {1} files hasn't been reached yet").format(
                str(max_logfiles), LOG_EXTENTSION)
            logging.info(log_msg)
            return
        else:
            log_to_cleanup = len(files) - max_logfiles

        if log_to_cleanup < 1:
            log_msg = str("No log files needs to be removed").format(
            )
            logging.info(log_msg)
            return
        else:
            files_to_remove = files[:log_to_cleanup]
            log_msg = str("{0} {1} file(s) to be removed").format(
                str(len(files_to_remove)), LOG_EXTENTSION)
            logging.info(log_msg)

        for file in files_to_remove:
            try:
                os.remove(file)
                log_msg = str("{0} successfully removed").format(file)
                logging.info(log_msg)
                counter += 1
            except OSError as err_cleanup_file:
                warn_msg = str("Remove: {0}").format(
                    err_cleanup_file)
                logging.warning(warn_msg)
        log_msg = str("Removed {0} {1} file(s)").format(
            str(counter), LOG_EXTENTSION)
        logging.info(log_msg)
    except Exception as err_cleanup:
        err_msg = str("Clean up exception: {0}").format(
            err_cleanup)
        logging.error(err_msg)


def logger(max_logfiles, log_root):
    try:
        log_root_path = path(log_root)
        if not os.path.exists(log_root_path):
            os.makedirs(log_root_path)
        log_filename = log_root_path + datetime.datetime.now().strftime(LOG_DATE_TIME_FORMAT) + \
            LOG_EXTENTSION
        logging.basicConfig(filename=log_filename, level=logging.DEBUG,
                            format='%(asctime)s;%(levelname)s;%(message)s')
        clean_up(max_logfiles, log_root_path)
    except Exception as err_logger:
        logging.error("Logger exception: %s", str(err_logger))
        raise err_logger
