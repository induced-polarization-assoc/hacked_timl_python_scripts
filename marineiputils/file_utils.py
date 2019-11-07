#!/bin/env python\
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA
"""
Set of file-handling utilities for the Marine IP Analysis application.
"""
from pathlib import Path
from pathlib import PurePath
import datetime


def make_data_dir_backup(data_folder_path, backup_path):
    """
    .. make_data_folder_backup(data_folder_path)

    :param data_folder_path:
        Path for the raw data folder as defined by the user via the GUI.
    :param backup_path:
        Path for the raw data backup folder -- essentially a copy of the target folder for the analysis.
    :return status:
        Success or failure status indicator code indicating if a backup was successful.
    """
    current_time = datetime.datetime.now().time()
    current_time = str(current_time)
    backup_dirname = PurePath(data_folder_path).name

    print(f"User has selected the path {backup_path} to save backups of the data files!")

    # backup_name = backup_dirname + "_backup" + iso_date + iso_time
    backup_name = backup_dirname + "_backup" + current_time
    print(backup_name)
    print(f"Now making a new backup directory called {backup_name} for you at {backup_path}...")
    backup_temp = Path.mkdir(backup_path, parents=False).rename(backup_name)

    # FIXME:  There is a problem with the main script when it comes to making this directory. It never
    # FIXME:    Gets past this point in the code. 
    backup_path = Path(backup_name)
    if Path.is_dir(backup_path):
        print("Success! The backup has been generated!")
    else:
        print("The backup failed to make the directory as anticipated.")


def construct_output_dir():
    """
    .. function:: construct_output_dir()
    Generates an output directory to save the reporting data in based on the path selected by the
    user GUI functions in the `mipgui' module.

    :return:
    """
    print("Right now it's not saving, but let's say it does... ")
    construct_output_filestruct()


def construct_output_filestruct():
    """
    Constructs the directory structure for the output data generated by the `ipSurvey` and `ipQuickShow`
    scripts (among others.)
    :return:
    """
    print("Let's pretend this got done, okay? Just keep this between us.")


def check_output_structure():
    """
    Validate the output file structure before copying the files over.
    :return:
    """
    pass


def copy_backup_files():
    """
    Copy the backup files from the folders over to an exact replica directory located at the
    site of the user's choosing.

    :return:
    """
    pass