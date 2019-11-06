#!/bin/env python
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA
"""
.. module:: file_dialogs

GUI functions for generating dialogues with the user to load data and display plots during data postprocessing and
analysis tasks.

__author__:  jjradler
__date__:   11/06/2019
"""
import os
import tkinter
import tkinter.filedialog
import tkinter.messagebox

root = tkinter.Tk()


def print_input_path(starting_dir):
    """
    .. function:: print_input_path()

    :Summary:
        Takes an input directory from the user using a dialog box with a reference to the root directory structure
        and the working directory chosen by the calling program.

    :param starting_dir:
        Working directory used as a reference for the dialog to start its user-interface within. Passed in from
        another module or function calling `print_input_path()` as user interface GUI.
    :return:
    """
    input_dir_to_scan = tkinter.filedialog.askdirectory(
        parent=root, initialdir=starting_dir,
        title='Select Directory to Scan'
        )
    print(f"Loading data from {input_dir_to_scan}!")    # TEST PRINT

    return input_dir_to_scan


def set_backup_path():
    """
    .. function:: print_input_path()

    :Summary:
        GUI window to prompt the user to select a backup location for their current raw dataset to avoid corruption

    :return:
    """
    current_dir = os.getcwd()
    backup_location = tkinter.filedialog.askdirectory(
        parent=root, initialdir=current_dir,
        title='Select Backup Location for Raw Data'
        )
    print(f"Backup location set at:\t {backup_location}!")  # TEST PRINT

    return backup_location


def save_yes_no():
    """
    .. function:: save_yes_no()

    :Summary:
        GUI window to prompt the user whether they will be saving the visualizations and charts generated by this
        processing/analysis run.

    :return answer:
        Yes or No saved as a True or False value.
    """
    question = "Would you like to save the plots generated by the analysis?"
    usr_says = tkinter.messagebox.askquestion('Save Plots?', question)

    if usr_says == 'yes':
        return set_save_path()

    else:
        verify = tkinter.messagebox.askquestion('You Sure?',
                                                'The temporary files generated will not be saved!',
                                                icon='warning'
                                                )
        if verify == 'yes':
            tkinter.messagebox.showinfo('FYI', 'OK, Moving on, then...')
            root.destroy()
            return None
        else:
            return set_save_path()


def set_save_path():
    """
    .. function:: print_input_path()

    :Summary:
        GUI window to prompt the user to select a save path for the analyzed/plotted data.

    :return:
    """
    current_dir = os.getcwd()
    save_location = tkinter.filedialog.askdirectory(
        parent=root, initialdir=current_dir,
        title='Select Save Location for Processed Data'
        )
    print(f"Save location set at:\t {save_location}!")    # TEST PRINT

    return save_location


if __name__ == "__main__":
    # What happens if this module is called as a standalone script.
    working_directory = os.getcwd()
    dir_to_scan = print_input_path(working_directory)
    backup_to = set_backup_path()
    save_plots = save_yes_no()
    print(working_directory)
    print(dir_to_scan)
    print(backup_to)
    print(save_plots)
