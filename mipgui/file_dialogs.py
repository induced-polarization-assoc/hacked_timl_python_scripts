#!/bin/env python
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA
"""
.. module:: file_dialogs

GUI functions for generating dialogues with the user to load data and display plots during data postprocessing and
analysis tasks.

__author__:  jjradler
__date__:   11/06/2019
"""
import tkinter
import tkinter.filedialog
import tkinter.messagebox
from pathlib import Path
import sys

import mipgui.yes_no_questions

root = tkinter.Tk()


def get_new_data():
    """
    .. function:: get_new_data()

    :Description:
        Takes an input directory from the user using a dialog box with a reference to the root directory structure
        and the working directory chosen by the calling program.

    :return input_data_to_process:
        Directory path to the top-level folder containing the `raw text` data files to be processed by
        the application.
    """
    input_data_to_process = tkinter.filedialog.askdirectory(
        parent=root, initialdir=Path.home(),
        title='Select Directory to Scan'
        )
    print(f"Loading data from {input_data_to_process}!")    # TEST PRINT

    return input_data_to_process


def set_backup_path(input_directory):
    """
    .. function:: get_new_data()

    :Summary:
        GUI window to prompt the user to select a backup location for their current raw dataset to avoid corruption

    :param input_directory:
        Path to the directory containing the data to be processed as defined by the user in previous
        dialogs.
    :return backup_location:
        Path object associated with the location to back up the original data files.
    """
    usr_says = mipgui.yes_no_questions.make_backup_yes_no(input_directory)
    if usr_says is True:
        print("You have opted to make a backup! Good thinking!")
        backup_location = tkinter.filedialog.askdirectory(parent=root,
                                                          initialdir=Path.cwd(),
                                                          title='Select Backup Location for Raw Data'
                                                          )
    else:
        verify = tkinter.messagebox.askquestion('You Sure?',
                                                'Your data will not be protected from possible corruption!',
                                                icon='warning'
                                                )
        if verify is 'yes':
            tkinter.messagebox.showinfo('Information', 'You have opted not to make a backup!')
            mipgui.file_dialogs.root.destroy()
            backup_location = None
        else:
            backup_location = mipgui.file_dialogs.set_backup_path()

    print(f"Backup location set at:\t {backup_location}!")  # TEST PRINT

    return backup_location


def set_save_path():
    """
    .. function:: get_new_data()

    :Summary:
        GUI window to prompt the user to select a save path for the analyzed/plotted data.

    :return:
    """
    save_location = tkinter.filedialog.askdirectory(
        parent=root, initialdir=Path.home(),
        title='Select Save Location for Processed Data'
        )
    print(f"Save location set at:\t {save_location}!")    # TEST PRINT

    return save_location


def shoreline_file_location(working_dir):
    """
    .. function shoreline_file_location()

    Prompts the user with a GUI to select a `*.shp` file, using the current working directory as a reference Point.

    :param working_dir:
        string --> Current working directory
    :return shoreline_file_path:
        string --> Shoreline file location path for data processing and rendering the output figure.
    """
    shoreline_file_path = tkinter.filedialog.askopenfilename(
        parent=root, initialdir=Path.home(),
        title='Select a Shoreline Shape File to Import',
        filetypes=[('shoreline files', '.shp')]
    )

    return shoreline_file_path


def set_analysis_prefs():
    """
    Set the preferences for parameters used in the analysis. Shows a number of radio buttons and entry fields.
    The "save_user_analysis_prefs()" function is run from within this function.
    :return:
    """
    plot_yesno = mipgui.yes_no_questions.analysis_yesno()
    if plot_yesno is True:
        print("Ok, so you want to actually DO something! ")
        pass
    else:
        print("Guess there's nothing to do then...")
        sys.exit()

    save_prefs = mipgui.yes_no_questions.save_user_analysis_prefs()
    if save_prefs:
        pass
    else:
        pass
