#!/bin/env python
#  Copyright (c) 2019. Induced Polarization Associates, LLC, Seattle, WA


class ProcOpts:
    """
    .. class:: ProcOpts

    .. synopsis:
        attributes of this object contain the user-defined processing method options.
    """
    def __init__(self):
        """
        constructor
        """
        self.save_this = []
        self.save_phase = True
        self.min_freq = 0
        self.max_freq = 0
        self.frequency_span = 200
        self.files_list = []


if __name__ == '__main__':
    procopts = ProcOpts
