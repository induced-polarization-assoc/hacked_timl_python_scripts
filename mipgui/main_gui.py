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
from timspackage.session import Session as Session
from timspackage.procopts import ProcOpts as ProcOpts
from timspackage.analysisopts import AnalysisOptions as AnalysisOptions

root = tkinter.Tk()

# tkinter.mainloop()


def main():
    """
    Main entry-Point using the GUI tools

    :return:
    """
    session = init_session()
    procopts = set_up_processing_options()
    analysisopts = choose_analysis_options()
    return session, procopts


def init_session():
    """
    Set user preferences upon starting up the program.
    #FIXME: Perhaps this data should be stored in an object for faster referencing throughout the application
    :return:
        session
    """
    session = Session()
    # prompt the user to select the directory containing the raw data to be processed.
    # session.process_yn = mipgui.yes_no_questions.new_data_yesno()
    session.raw_data_path = mipgui.yes_no_questions.new_data_yesno()
    if session.raw_data_path is not None:
        print(f"The directory containing files to process is {session.raw_data_path}")
        # backup_location = mipgui.file_dialogs.set_backup_path(dir_to_process)
        # if backup_location is not None:
        #     # make the backups automagically.
        #     marineiputils.file_utils.make_data_dir_backup(dir_to_process, backup_location)
        session.select_files = mipgui.file_dialogs.select_files_for_processing()
        session.pickle_path = mipgui.file_dialogs.set_pickle_path()
    else:
        session.raw_data_path = None
        print("Nothing to do here, then. Moving on to analysis...")
        session.pickle_path = mipgui.file_dialogs.open_existing_pickle()

    # SET THE ANALYSIS PREFERENCES FOR THE SESSION
    session.output_path = mipgui.yes_no_questions.save_yes_no()
    mipgui.file_dialogs.set_analysis_prefs()

    return session


def set_up_processing_options():
    """

    :returnprocopts:

    """
    procopts = ProcOpts()
    procopts.
    return procopts


def choose_analysis_options():
    """

    :return analysisopts:

    """
    analysisopts = AnalysisOptions()
    return analysisopts


if __name__ == "__main__":
    process, pickle, output = main()
