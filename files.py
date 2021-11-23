import shutil
import os
import traceback
import logging
from datetime import datetime, timedelta
from utils import operating_system


if not getattr(__builtins__, "WindowsError", None):
    class WindowsError(OSError):
        pass


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
    # Loop through folder
    for from_file in get_files(from_folder):
        total_counter += 1
        to_file = from_file.replace(from_folder, to_folder)
        # Create folder if not exist
        if not os.path.exists(os.path.dirname(to_file)):
            os.makedirs(os.path.dirname(to_file))
        # (Try to) move the file
        try:
            os.rename(from_file, to_file)
            moved_files.append(to_file)
            moved_counter += 1
        # Filer som er åpne / skrives vil spytte ut en WindowsError. Ignorer disse
        except WindowsError as win_err:
            logging.warning(
                f'File {0} is open/in use. Windows error: {1}'.format(to_file, win_err))
    return moved_files


def remove_archive(timelimit, archive_root, prefix, extenstion, timestamp_format):
    for (filepath, foldername, _) in os.walk(archive_root):
        try:
            # Archive root subfolders
            if operating_system() == "windows":
                archive_list = [filepath + '\\' +
                                folder for folder in foldername]
            else:
                archive_list = [filepath + '/' +
                                folder for folder in foldername]

            # Remove old archives
            for archive in archive_list:
                if operating_system() == "windows":
                    archived = archive[len(archive)-archive[::-1].find('\\'):]
                else:
                    archived = archive[len(archive)-archive[::-1].find('/'):]

                archived_no_prefix = archived.replace(prefix, "")
                archived_no_extenstion = archived_no_prefix.replace(
                    extenstion, "")
                archived_time = datetime.strptime(
                    archived_no_extenstion, timestamp_format)
                timelimit_timestamp = datetime.now() - timedelta(hours=timelimit)

                log_msg = str("Remove archive files older than {0}").format(
                    timelimit_timestamp)
                logging.info(log_msg)
                if archived_time < timelimit_timestamp:
                    try:
                        log_msg = "Removing '%s'", archive
                        logging.info(log_msg)
                        shutil.rmtree(archive)
                    except shutil.Error as err:
                        log_warning_msg = f"Failed to remove '{0}'. Exception: {1}".format(
                            archive, err)
                        logging.warning(log_warning_msg)

            break
        except Exception as err_remove_archives:
            traceback.print_stack()
            raise err_remove_archives
