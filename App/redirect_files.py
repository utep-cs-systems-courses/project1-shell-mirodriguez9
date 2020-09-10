"""Redirect files."""
import os
import re
import sys
import tempfile
from module_config import SHELL_LOG as log
from App import command_files
#from command_files import *
#from command_files import execute_command
#from command_files import clean_background_command
#from filename import method

def redirect_execute_output(command, background=False):
    """Execute command as a redirect output.
        :param command: Command to be redirected. E.g. ls > out.txt"""
    log.info("Redirect output command: %s" % command)

    # Fork shell and Redirect
    shell_pid = os.fork()
    if shell_pid < 0:  # failure
        log.critical("Shell fork redirect %s failed" % shell_pid)
    elif shell_pid == 0:  # Child redirect
        os.close(1)
        sys.stdout = open(f"{command[1]}", "w")  # Create file
        stdout_fd = sys.stdout.fileno()  # Create file descriptor to stdout
        os.set_inheritable(stdout_fd, True)
        log.info("redirect: '%s' > '%s'" % (command[0], command[1]))
        command_files.execute_command(re.split(" ", command[0]))
    else:  # Parent
        status = os.wait()
        log.info("Terminated redirect output process id: %d", status[0])
        log.debug("Signal number that ended redirect output %d", status[1])
        return 0
    return 0


def redirect_execute_input(command, background=False):
    """Execute command as a redirect input.
        :param command: Command to be redirected. E.g. cat < out.txt"""
    log.info("Redirect input command: %s" % command)
    if background:
        command = command_files.clean_background_command(command)

    # Fork shell and Redirect
    shell_pid = os.fork()
    if shell_pid < 0:  # failure
        log.critical("Shell fork redirect %s failed" % shell_pid)
    elif shell_pid == 0:  # Child redirect
        os.close(0)
        sys.stdin = open(f"{command[1]}", "r")  # Create file
        stdin_fd = sys.stdin.fileno()  # Create file descriptor to stdout
        os.set_inheritable(stdin_fd, True)
        log.info("redirect: '%s' < '%s'" % (command[0], command[1]))
        command_files.execute_command(re.split(" ", command[0]), background)
    else:  # Parent
        status = os.wait()
        log.info("Terminated redirect input process id: %d", status[0])
        log.debug("Signal number that ended redirect input %d", status[1])
        return 0
    return 0

def clean_program_stdout(stdout):
    """Cleans the standard output from a process."""
    stdout = [x.replace(" ", "") for x in stdout]
    stdout = " ".join(stdout)
    stdout = stdout.strip()
    stdout = re.sub("\n", "", stdout)
    return stdout
