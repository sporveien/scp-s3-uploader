import shutil
import os
import traceback
import logging
from datetime import datetime, timedelta
from utils import operating_system


if not getattr(__builtins__, "WindowsError", None):
    class WindowsError(OSError):
        pass


def get_subfolders(root_folder):
    try:
        all_files = []
        for (file_path, dirs, files) in os.walk(root_folder):
            if operating_system() == "windows":
                all_files += [file_path + '\\' + dir for dir in dirs]
            else:
                all_files += [file_path + '/' + dir for dir in dirs]
        return all_files
    except Exception as err_get_files:
        traceback.print_stack()
        raise err_get_files


def get_files(root_folder):
    try:
        all_files = []
        for (file_path, _, files) in os.walk(root_folder):
            if operating_system() == "windows":
                all_files += [file_path + '\\' + file for file in files]
            else:
                all_files += [file_path + '/' + file for file in files]
        return all_files
    except Exception as err_get_files:
        traceback.print_stack()
        raise err_get_files


def move_files(from_folder, to_folder):
    total_counter = 0
    moved_counter = 0
    moved_files = []
    log_msg = str("Start move files from {0} to folder {1}").format(
        from_folder, to_folder)
    logging.debug(log_msg)
    # Loop through folder
    for from_file in get_files(from_folder):
        total_counter += 1
        to_file = from_file.replace(from_folder, to_folder)

        # Create folder if not exist
        if not os.path.exists(os.path.dirname(to_file)):
            os.makedirs(os.path.dirname(to_file))
        # (Try to) move the file
        try:
            log_msg = str("Move {0}").format(from_file)
            logging.info(log_msg)
            os.rename(from_file, to_file)
            log_msg = str("Successfully moved to {0}").format(to_file)
            logging.info(log_msg)
            moved_files.append(to_file)
            moved_counter += 1
        # Filer som er åpne / skrives vil spytte ut en WindowsError. Ignorer disse
        except WindowsError as win_err:
            logging.warning(
                f'File {0} is open/in use. Windows error: {1}'.format(to_file, win_err))
    return moved_files


def remove_archive(timelimit, archive_root, prefix, suffix, timestamp_format, remove_archive_dir):
    cleaned_up = []
    for (path, sub_dirs, files) in os.walk(archive_root):
        if remove_archive_dir:
            for dir in sub_dirs:
                if dir.startswith(prefix) and dir.endswith(suffix):
                    timestamp = dir.replace(prefix, "").replace(suffix, "")
                    archived_timestamp = datetime.strptime(
                        timestamp, timestamp_format)
                    timelimit_timestamp = datetime.now() - timedelta(hours=timelimit)

                    if archived_timestamp and timelimit_timestamp:
                        if archived_timestamp < timelimit_timestamp:
                            try:
                                archive_path_to_remove = os.path.join(
                                    path, dir)

                                log_msg = str("Archive {0} have exceeded archive retention time which is set to {1} hour(s) in .yml config file.").format(
                                    archive_path_to_remove, timelimit)
                                logging.info(log_msg)
                                log_msg = str(
                                    "Remove {0}").format(archive_path_to_remove)
                                logging.info(log_msg)

                                shutil.rmtree(archive_path_to_remove)
                                cleaned_up.append(archive_path_to_remove)

                                log_msg = str(
                                    "Successfully removed {0}").format(archive_path_to_remove)
                                logging.info(log_msg)
                            except Exception as err:
                                err_msg = str(
                                    "Failed to remove archive {0}. Exception {1}").format(archive_path_to_remove, err)
                                logging.error(err_msg)
                                traceback.print_stack()
                                raise err_msg
                        else:
                            log_msg = str("Archive {0} has not exceeded archive retention time {1}").format(
                                dir, timelimit)
                            logging.info(log_msg)
                    else:
                        log_warning = str("Failed to build date and time from directory {0} timestamp, format set to {1} in .yml config").format(
                            dir, timestamp_format)
                        logging.warning(log_warning)
                else:
                    log_warning = str(
                        "Directory {0} does not start with prefix {1} and/or suffix {2}").format(dir, prefix, suffix)
                    logging.warning(log_warning)
        else:
            for file in files:
                file_no_ext = str(os.path.basename(
                    os.path.splitext(file)[0])).format()
                if file_no_ext.startswith(prefix) and file_no_ext.endswith(suffix):
                    try:
                        timestamp = file.replace(
                            prefix, "").replace(suffix, "")
                        archived_timestamp = datetime.strptime(
                            timestamp, timestamp_format)
                        timelimit_timestamp = datetime.now() - timedelta(hours=timelimit)
                    except Exception as err:
                        log_warning = str("Failed to build date and time from directory {0}. Exception: {1}").format(
                            file, err)
                        logging.warning(log_warning)
                    else:
                        if archived_timestamp and timelimit_timestamp:
                            if archived_timestamp < timelimit_timestamp:
                                try:
                                    archive_path_to_remove = os.path.join(
                                        path, file)

                                    log_msg = str("Archive {0} have exceeded archive retention time which is set to {1} hour(s) in .yml config file.").format(
                                        archive_path_to_remove, timelimit)
                                    logging.info(log_msg)
                                    log_msg = str(
                                        "Remove {0}").format(archive_path_to_remove)
                                    logging.info(log_msg)

                                    shutil.rmtree(archive_path_to_remove)
                                    cleaned_up.append(archive_path_to_remove)

                                    log_msg = str(
                                        "Successfully removed {0}").format(archive_path_to_remove)
                                    logging.info(log_msg)
                                except Exception as err:
                                    err_msg = str(
                                        "Failed to remove archive {0}. Exception {1}").format(archive_path_to_remove, err)
                                    logging.error(err_msg)
                                    traceback.print_stack()
                                    raise err_msg
                            else:
                                log_msg = str("Archive {0} has not exceeded archive retention time {1}").format(
                                    file, timelimit)
                                logging.info(log_msg)
                        else:
                            log_warning = str("Failed to build date and time from directory {0} timestamp, format set to {1} in .yml config").format(
                                file, timestamp_format)
                            logging.warning(log_warning)
                else:
                    log_warning = str(
                        "file {0} does not start with prefix {1} and/or suffix {2}").format(file, prefix, suffix)
                    logging.warning(log_warning)
    return cleaned_up
