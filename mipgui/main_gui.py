#!/bin/env python

#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA

# mipgui/main_gui.py
"""
Docstring
#TODO: ALWAYS ALWAYS ALWAYS ADD A DOCSTRING! 
"""
import tkinter
from pathlib import Path
from tkinter import messagebox
# from pathlib import PurePath

import mipgui.file_dialogs
import marineiputils.file_utils
import mipgui.yes_no_questions

# import timspackage.ipSurvey

root = tkinter.Tk()

# tkinter.mainloop()


def main():
    """
    Main entry-Point using the GUI tools

    :return:
    """
    init_session()
    analysis_session()


def init_session():
    """
    Set user preferences upon starting up the program.
    #FIXME: Perhaps this data should be stored in an object for faster referencing throughout the application
    :return:
    """
    # prompt the user to select the directory containing the raw data to be processed.
    dir_to_process = mipgui.yes_no_questions.new_data_yesno()
    if dir_to_process is not None:
        print(f"The directory containing files to process is {dir_to_process}")
        backup_location = mipgui.file_dialogs.set_backup_path(dir_to_process)

        # make the backups automagically.
        marineiputils.file_utils.make_data_dir_backup(dir_to_process, backup_location)
    else:
        print("Nothing to do here, then. Moving on to analysis...")

    # SET THE ANALYSIS PREFERENCES FOR THE SESSION
    mipgui.file_dialogs.set_analysis_prefs()

    # PROMPT THE USER IF THEY WANT TO SAVE THE OUTPUT AND IF SO, WHERE?
    output_directory = mipgui.yes_no_questions.save_yes_no()
    if output_directory is None:
        print("There's really no point in just pulling the stuff up without saving it is there?")
    else:
        print(f"Saving the output of this analysis to the directory path: {output_directory}")
        marineiputils.file_utils.construct_output_dir()
        marineiputils.file_utils.check_output_structure()


def analysis_session():
    """
    Actual analysis calls to the appropriate scripts.
    :return:
    """
    print("Now performing analysis on the processed data as requested.")
    # timspackage.ipSurvey()


if __name__ == "__main__":
    main()
