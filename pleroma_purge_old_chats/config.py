#!/usr/bin/env python

import sys
try:
    if sys.version_info.major >=3 and sys.version_info.minor >= 10:
        from importlib.resources import files
    else:
        from importlib_resources import files
except ImportError as e:
    print("ERROR:", e.args)
import os    
from configparser import ConfigParser


def config(filename=None):
    if filename is None:
        filename = 'database.ini'
        module = None
        try:
            module = files('pleroma_purge_old_chats.data')
            filename_path = module.joinpath(filename)
        except Exception:
            # isn’t compatible with PEP 302
            print('As a fallback, try using os.path to find the .ini (is "importlib_resources" installed by pip?)')
            filename_path = os.path.join(os.path.dirname(__file__), 'data', filename)
            print("bundled config filename:", filename_path)
            filename_path = os.path.abspath(filename_path)
    else:
        filename_path = filename

    #print("\nfilename:", filename_path)

    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename_path)
    return parser
