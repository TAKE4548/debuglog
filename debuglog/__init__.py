# !/usr/bin/env/ python3
# -*- coding: utf-8 -*-

from .debuglog import set_fhandler_format, set_shandler_format, \
    get_debug_logger, calledlog
from .measuretime import time_record, get_measurer, pop_measurer

__version__ = "0.0.1b"
