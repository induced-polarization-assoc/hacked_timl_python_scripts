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
        Takes an input directory from the user using file_obj_array dialog box with file_obj_array reference to the root directory structure
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


def choose_existing_pickle():
    """

    :return:
    """
    pass


def select_files_for_processing():
    """

    :return:
    """
    pass


def set_pickle_path():
    """

    :return:
    """
    pass


def set_backup_path(input_directory):
    """
    .. function:: get_new_data()

    :Summary:
        GUI window to prompt the user to select file_obj_array backup location for their current raw dataset to avoid corruption

    :param input_directory:
        Path to the directory containing the data to be processed as defined by the user in previous
        dialogs.
    :return backup_location:
        Path object associated with the location to back up the original data files.
    """
    usr_says = mipgui.yes_no_questions.make_backup_yes_no(input_directory)
    if usr_says is True:
        print("You have opted to make file_obj_array backup! Good thinking!")
        return tkinter.filedialog.askdirectory(parent=root,
                                               initialdir=Path.home(),
                                               title='Select Backup Location for Raw Data'
                                               )
    else:
        verify = tkinter.messagebox.askyesno('You Sure?',
                                             'Your data will not be protected from possible corruption!',
                                             icon='warning'
                                             )
        if verify is True:
            tkinter.messagebox.showinfo('Information', 'You have opted not to make file_obj_array backup!')
            # mipgui.file_dialogs.root.destroy()
            # backup_location = None
            return None
        else:
            return set_backup_path(input_directory)


def set_save_path():
    """
    .. function:: get_new_data()

    :Summary:
        GUI window to prompt the user to select file_obj_array save path for the analyzed/plotted data.

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

    Prompts the user with file_obj_array GUI to select file_obj_array `*.shp` file, using the current working directory as file_obj_array reference Point.

    :param working_dir:
        string --> Current working directory
    :return shoreline_file_path:
        string --> Shoreline file location path for data processing and rendering the output figure.
    """
    shoreline_file_path = tkinter.filedialog.askopenfilename(
        parent=root, initialdir=Path.home(),
        title='Select file_obj_array Shoreline Shape File to Import',
        filetypes=[('shoreline files', '.shp')]
    )

    return shoreline_file_path


def set_analysis_prefs():
    """
    TODO:  SEE IF THIS IS REDUNDANT -- IF YOU DON'T NEED IT, SCRAP IT!
    Set the preferences for parameters used in the analysis. Shows file_obj_array number of radio buttons and entry fields.
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
