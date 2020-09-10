"""Command file."""
import os
import re
import sys
import tempfile
from module_config import *
from App import pyutils
from App import user_files
from App import exec_files
from App import redirect_files
from module_config import shell_log as log
#from pyutils import get_environ_paths
#from user_files import clean_user_input
#from user_files import check_user_input_is_empty
#from exec_files import change_directory
#from exec_files import pipe_execute
#from exec_files import fork_execute
#from redirect_files import redirect_execute_output
#from redirect_files import redirect_execute_input
#from background_files import background_execute
#from filename import method

def convert_to_command(command):
    """Converts a command to a pipe or redirect command."""
    joined = ' '.join(command)
    return re.split(re.compile(r'\s[><&|]\s'), joined)

def clean_background_command(command):
    """Cleans a command containing background &.
        :param command: Converted command e.g. ['bash', '$PWD/c1 &']."""
    return [x.replace(" &", "") for x in command]

def command_mannager(command):
    """Manages commands to either skip, fork, or pipe."""
    # Clean user input
    log.debug("User input: %s" % command)
    command = user_files.clean_user_input(command)

    # Check for empty and do nothing
    if check_user_input_is_empty(command):
        log.warning("Command is empty. Waiting for next command.")
        return -1

    # Terminate if exit command
    if "exit" in command:
        log.info("Exit command found. Exiting.")
        sys.exit(1)

    # cd command
    if "cd" in command:
        log.info("cd command found.")
        exec_files.change_directory(command[1])
        return 0

    # Check if there is a pipe
    if "|" in command:
        command = convert_to_command(command)
        return_code = exec_files.pipe_execute(command)
        # Single pipes should return two times. With -1 and 0
        log.debug("Pipe finished with return code: %d" % return_code)
        return return_code

    if "&" in command:
        # Send to background after redirecting stdout
        if ">" in command:
            command = convert_to_command(command)
            return_code = redirect_files.redirect_execute_output(command)
            # Redict should return two times. With -1 and 0
            log.debug("Redirect finished with return code: %d" % return_code)
            return return_code
        # Send to background after redirecting stdin
        if "<" in command:
            log.warning("background detected!")
            command = convert_to_command(command)
            return_code = redirect_files.redirect_execute_input(command, background=True)
            # Redict should return two times. With -1 and 0
            log.debug("Redirect finished with return code: %d" % return_code)
            return return_code
        command = convert_to_command(command)
        command = clean_background_command(command)
        background_files.background_execute(command)

    # Check if there is an output redirect
    if ">" in command:
        command = convert_to_command(command)
        return_code = redirect_files.redirect_execute_output(command)
        # Redict should return two times. With -1 and 0
        log.debug("Redirect finished with return code: %d" % return_code)
        return return_code

    if "<" in command:
        command = convert_to_command(command)
        return_code = redirect_files.redirect_execute_input(command)
        # Redict should return two times. With -1 and 0
        log.debug("Redirect finished with return code: %d" % return_code)
        return return_code

    # run as fork
    fork_execute(command)
    return 0


def execute_command(command, background=False):
    """Executes a command.
        Looks for the command in the environ $PATH if not given as path.
        :param command: User command as list to be run as bash shell."""
    # Get paths from enviroment variable
    paths = pyutils.get_environ_paths()
    is_command_path = user_files.check_user_input_is_path(command)
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
                if background:
                    os.write(2, f"Running {command} in background".encode())
                    bg = os.spawnve(os.P_NOWAIT, program_loc, command, os.environ)
                    return bg
                else:
                    os.execve(program_loc, command, os.environ)
            except FileNotFoundError:
                log.debug("Command not found in path: %s" % path)
            except PermissionError:
                log.debug("Command permission denied in path: %s" % path)
        log.warning("Command %s not found anywhere in $PATH" % command[0])
        os.write(2, f"{command[0]}: command not found\n".encode())

    # Kill zombies
    os.kill(os.getpid(), 9)
