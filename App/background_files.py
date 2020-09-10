"""Background files."""
import os
import re
import sys
import tempfile
from module_config import SHELL_LOG as log
from App import command_files
from App import redirect_files
from App import pyutils
from App import user_files
from command_files import convert_to_command
from redirect_files import redirect_execute_output
from pyutils import get_environ_paths
from user_files import check_user_input_is_path
#from filename import method

def background_execute(command):
    # Get paths from enviroment variable
    paths = pyutils.get_environ_paths()
    is_command_path = user_input.check_user_input_is_path(command)
    log.info("Executing command: %s" % command)

    # Run command directly as path
    if is_command_path:
        program_loc = f"{command[0]}"
        log.debug("Command as path %s to be executed" % program_loc)
        try:
            os.execve(program_loc, command, os.environ)
        except FileNotFoundError:
            os.write(2, f"{program_loc}: command not found\n".encode())
            log.warning("Command not found in %s" % program_loc)
            return -1

    # If the command is not a path
    else:
        for path in paths:
            program_loc = f"{path}/{command[0]}"
            log.debug("Trying to execute %s in dir: %s" % (command[0], path))
            try:
                # Run to background and return pid
                bg = os.spawnve(os.P_WAIT, program_loc, command, os.environ)
                os.write(2, f"Background process exit code: {bg}".encode())
                return bg
            except FileNotFoundError:
                log.debug("Command not found in path: %s" % path)
            except PermissionError:
                log.debug("Command permission denied in path: %s" % path)
        log.warning("Command %s not found anywhere in $PATH" % command[0])
        os.write(2, f"{command[0]}: command not found\n".encode())


def background_execute_manager(command, redirect_to=None):
    """Manager for background processes."""
    if ">" in command:
        command = command_files.convert_to_command(command)
        return_code = command_files.redirect_execute_output(command)
        return_code = background_execute(command, redirect_to="output")
    if "<" in command:
        pass
