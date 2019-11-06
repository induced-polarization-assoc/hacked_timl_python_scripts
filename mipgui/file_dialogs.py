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
    print(f"Loading data from {input_dir_to_scan}!")

    return input_dir_to_scan


if __name__ == "__main__":
    # What happens if this module is called as a standalone script.
    working_directory = os.getcwd()
    print_input_path(working_directory)
