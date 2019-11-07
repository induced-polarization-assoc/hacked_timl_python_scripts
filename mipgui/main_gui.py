#!/bin/env python

#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA

# mipgui/main_gui.py
"""
Docstring
#TODO: ALWAYS ALWAYS ALWAYS ADD A DOCSTRING! 
"""
import tkinter
from pathlib import Path
# from pathlib import PurePath

import mipgui.file_dialogs
import marineiputils.file_utils

root = tkinter.Tk()


def main():
    """
    Main entry-Point using the GUI tools

    :return:
    """
    init_session_preferences()
    set_analysis_preferences()


def init_session_preferences():
    """
    Set user preferences upon starting up the program.
    #FIXME: Perhaps this data should be stored in an object for faster referencing throughout the application
    :return:
    """
    working_directory = Path.cwd()
    dir_to_scan = mipgui.file_dialogs.print_input_path(working_directory)
    backup_to = mipgui.file_dialogs.set_backup_path()
    marineiputils.file_utils.make_data_dir_backup(dir_to_scan, backup_to)
    save_plots = mipgui.file_dialogs.save_yes_no()
    # TODO: make a file utility that makes the save directory with the appropriate structure for analysis
    print(working_directory)
    print(dir_to_scan)
    print(backup_to)
    print(save_plots)


def set_analysis_preferences():
    """
    #FIXME: Perhaps this data should be stored in an object for faster referencing throughout the application
    Set user preferences for analysis output.

    :return:
    """
    pass


if __name__ == "__main__":
    main()
