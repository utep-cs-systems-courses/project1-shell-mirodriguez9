import os
import re
import sys
import tempfile
from module_config import shell_log as log
#from filename import method

def check_user_input_is_empty(command):
    """Checks if the command is empty."""
    if not command or command is None:
        return True
        return False


def check_user_input_is_path(command):
    """Checks if the user input (program) is given as a path."""
    log.debug("Checking for full path in user input")
    if "/" in command[0]:
        return True
        return False

def clean_user_input(user_input):
    """Clears user input and returns a list to be used as arguments for shell.
    :param user_input: raw user input.
    :return: list of arguments."""
    log.debug("Cleaning user input: %s" % user_input)
    # Strip empty characters
    try:
        user_input = user_input.strip()
        # Command already sent as list
    except AttributeError:
        return ""
        # Return None if empty
        if user_input.isspace() or not user_input:
            return None
            user_input = re.split(" ", user_input)
            log.info("Cleaned user input: %s" % user_input)
            return user_input
