"""Shell implementation using python3."""
import os
import sys
from App import user_files
from App import exec_files
from module_config import SHELL_LOG as log
#from user_files import clean_user_input

from Logger.logging_config import get_simple_logger

log = get_simple_logger("shell_log")


def set_ps1(user_ps1=None):
    """Set PS1 if not set."""
    # Set to user ps1
    if user_ps1:
        log.info('Setting PS1 to %s', user_ps1)
        os.environ['PS1'] = user_ps1
        return

    # Set to default
    if 'PS1' not in os.environ:
        log.info("PS1 not found in env")
        log.info("Setting PS1 to $ ")
        os.environ['PS1'] = "$ "
        return
    os.environ['PS1'] = "$ "
    return


# def looper(times=2):
#     """Loops user input for command ever if needed."""

def main():
    # Set ps1
    set_ps1()
    # Output PS1 to console
    os.write(2, (os.environ['PS1']).encode())

    # While until exit
    terminate = False
    while not terminate:
        # Get user input
        try:
            user_input = input()
        except EOFError:
            # user_input = input()
            pass
        log.debug("User input: %s" % user_input)
        user_input = user_files.clean_user_input(user_input)

        # Exit command
        if "exit" in user_input:
            sys.exit(0)

        # Fixes bash script empty commands
        if user_input == "":
            os.write(2, (os.environ['PS1']).encode())
            continue

        # Run command
        exec_files.forker_executer(user_input)

        # Output PS1 to console
        os.write(2, (os.environ['PS1']).encode())
