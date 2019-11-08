#!/bin/env python
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA


class Session:
    """
    .. class:: Session
    Data structure containing the temporary session information input by the user.

    .. attributes:
    username = string
    process_yn = bool
    raw_data_path = (path/str)
    backup_data_path =  (path/str)
    process_methods_selected = [str, str,...]
    save_phases = bool
    processed_data_path = (path/str)
    save_these = [(str),(str)...]
    select_files = [int, int, ...]
    pickle_path = (path/str)
    output_path = (path/str)
    logs_path = (path/str)
    """
    # TODO: Add the session attributes and init method here to instantiate the object.

    def __init__(self):
        """
        Constructor for the Session -- creates only one session object per operator session (idk how to
        do this yet, but I'll figure that part out later.)

        """
        self.username = None
        self.process_yn = True
        self.raw_data_path = None
        self.backup_data_path = None
        self.pickle_path = None
        self.processed_data_path = None
        self.output_path = None
        self.select_files = []
        self.save_phases = True
        self.save_these = ['zAnyF', 'raw', 'upsideDown']
        self.logs_path = None


if __name__ == '__main__':
    session = Session()
