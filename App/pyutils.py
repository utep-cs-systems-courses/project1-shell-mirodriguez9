"""Utilities file."""
import os
import re
import sys
import tempfile
from module_config import SHELL_LOG as log
#from filename import method

def get_environ_paths():
    """Creates a list with pats to find commands."""
    log.debug("Getting paths from os.environ")
    environ = os.environ
    return re.split(":", environ['PATH'])
