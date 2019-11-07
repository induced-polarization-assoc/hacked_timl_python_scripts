#!/bin/env python\
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA
"""
Set of file-handling utilities for the Marine IP Analysis application.
"""
from pathlib import Path
from pathlib import PurePath
from datetime import date
from datetime import time


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
    today = date.today()
    now = time.now()
    iso_date = date(today).isoformat()
    iso_time = now

    backup_dirname = PurePath(data_folder_path).name

    print(f"User has selected the path {backup_path} to save backups of the data files!")

    backup_name = backup_dirname + "_backup" + iso_date + iso_time
    print(backup_name)
    print(f"Now making a new backup directory called {backup_name} for you at {backup_path}...")
    Path.mkdir(backup_path, parents=False).rename(backup_name)

    if Path.is_dir(backup_name):
        return 0
    else:
        return 1


def construct_save_dir():
    """
    .. function:: construct_output_dir()
    Generates an output directory to save the reporting data in based on the path selected by the
    user GUI functions in the `mipgui' module.

    :return:
    """
    pass


