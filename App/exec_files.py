"""Execute file."""
import os
import re
import sys
import tempfile
from module_config import SHELL_LOG as log
from App import command_files
#from command_files import execute_command
#from filename import method

def change_directory(path):
    """Changes current directory.
        :param path: Path to change current directory"""
    try:
        os.chdir(path)
    except FileNotFoundError:
        log.warning("Cannot change path to: %s" % path)
        os.write(2, f"{path}: No such file or directory\n".encode())
    return os.getcwd()

def fork_execute(command):
    """Creates a fork and executes a command.
        :param command: User command as list to be run as shell."""
    log.info("Fork execute command: %s" % command)

    fork = os.fork()  # Create fork

    # Fork failure
    if fork < 0:
        log.critical("fork %s failed" % fork)
    # Fork child
    elif fork == 0:
        command_files.execute_command(command)
    # Fork Parent
    else:
        status = os.wait()
        log.info("Terminated child's process id: %d", status[0])
        log.debug("Signal number that ended child: %d", status[1])
        return 0
    return 0


def pipe_execute(command):
    """Execute command as a pipe.
        :param command: Command to be executed. E.g. ls | grep .py"""
    log.info("Pipe command: %s" % command)
    stdin = sys.stdin.fileno()  # usually 0
    stdout = sys.stdout.fileno()  # usually 1
    pipe_in, pipe_out = os.pipe()  # Create pipe

    # Fork shell and pipe
    shell_pid = os.fork()
    pipe_pid = os.fork()

    # Get into shell fork
    if shell_pid < 0:
        log.critical("Fork shell %s failed" % shell_pid)
    elif shell_pid == 0:  # Shell Children
        log.info("Comand received for pipe: %s", command)

        # Get into pipe fork
        if pipe_pid < 0:
            log.critical("Fork pipe %s failed" % pipe_pid)

        elif pipe_pid == 0:  # Child pipe process
            os.close(pipe_in)
            os.close(stdin)
            os.dup2(pipe_out, stdout)
            log.info("Child pipe command: %s", command[0])
            command_files.execute_command(re.split(" ", command[0]))

        else:  # Parent pipe process
            os.close(pipe_out)
            os.dup2(pipe_in, stdin)

            status = os.waitpid(pipe_pid, 0)
            log.info("Terminated pipe child's process id: %d", status[0])
            log.debug("Signal number that ended pipe child: %d", status[1])

            log.info("Parent pipe command: %s" % command[1])
            command_files.execute_command(re.split(" ", command[1]))

    else:  # Shell Parent
        os.close(pipe_in)
        os.close(pipe_out)
        try:
            status = os.waitpid(shell_pid, 0)
            log.info("Terminated pipe parent's process id: %d", status[0])
            log.debug("Signal number that ended pipe parent: %d", status[1])
        except ChildProcessError:
            # Signal that shell copy has ended
            return -1

    # Kill zombies
    os.kill(pipe_pid, 9)
    return 0
