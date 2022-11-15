import os
import subprocess
from shutil import which
import re

MAJOR_VERSION = '0'
MINOR_VERSION = '0'
PATCH_VERSION = '1'
VERSION = MAJOR_VERSION + MINOR_VERSION + PATCH_VERSION


# GOAL:
#  1) automate the parallel performance analysis of the binaries (C/C++/Fortran)
#  2) invoke analysis using provided range of tasks/processes with optionally
#     specified step (e.g. 1..32:1)
#  3) in case of MPI code, detect MPI vendor (OMP/IMPI) and test advanced MPI
#     collective optimization via envars. use the most optimal execution from the
#     previous step
#  4) test different compiler flags
#  5) plot graphs of scalability (step 2), histograms of collective calls (step 3),
#     and histograms of compiler flags (step 4)
#
#
#
# TODO:
#  - take binary name as an input parameter
#  - write batch script based on specification from the command line


def print_msg_with_header(msg_header, msg):
    """
    Print a message with a header to terminal
    :param msg_header: Header of the message
    :param msg: Message body
    :return: None
    """
    print(msg_header, end=' ')
    print(msg)


def print_dbg_info(msg):
    """
    Print a debug message to terminal
    :param msg: Message body
    :return: None
    """
    msg_header = "== DEBUG =="
    if __debug__:
        print_msg_with_header(msg_header, msg)


def print_err_info(msg):
    """
    Print an error message to terminal
    :param msg: Message body
    :return: None
    """
    msg_header = "== ERROR =="
    print_msg_with_header(msg_header, msg)


def is_available(name):
    """
    Check whether program `name` exists in a PATH or not
    """
    return which(name) is not None


def get_version_from_text(text):
    """
    Get version in a form X.Y.Z from a text
    :param text: Input string
    :return: String that stores version in a form of X.Y.Z
    """
    # FIXME: This implementation doesn't consider characters
    #        in the version names and possibly multiple versions
    #        indicated in the provided text. It simply picks up
    #        the first 3 digits and concatenate them with '.'.
    #        There should be a better, more versatile implementation.
    version = re.findall(r'\d+', text)
    if not version:
        version = ['?'] * 3
    return '.'.join(version[0:3])


def print_version(app, text):
    """
    Simply reports a version name of the 'app' to the console
    :param app: Application name
    :param text: Text that has a version name in it
    :return: None
    """
    print(app + ' version: ' + get_version_from_text(text))


def dump_to_file(filename, text):
    """
    Dump text to file
    :param filename: File name
    :param text: Text to write
    :return: None
    """
    file = open(filename, 'w')
    file.write(text)
    file.close()


def load_modules(module_list):
    # Load modules
    if len(module_list) > 0:
        if is_available('module'):
            subprocess.run(['module', 'purge'])
            for module in module_list:
                subprocess.run(['module', 'load', module])

        else:
            print_err_info('A module list was specified but there is '
                           'no \'module\' command available')


def execute_app(app_name, app_keys):
    """
    Execute application with provided keys
    :param app_name: Name of the application
    :param app_keys: String of keys
    :return: Stdout after execution
    """
    result = subprocess.run([app_name, app_keys], stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
    return result.stdout.decode('utf-8')


def report_statistics(module_list):
    """
    Report information about the system, compilers and libraries
    :param module_list: List of modules to be loaded
    :return: None
    """
    list_of_apps = [('uname', '-o'), ('uname', '-r'), ('uname', '-m'),
                    ('module', '--version'), ('mpirun', '--version'),
                    ('gcc', '--version'), ('g++', '--version'), ('gfortran', '--version'),
                    ('icc', '--version'), ('icpc', '--version'), ('ifort', '--version'),
                    ('clang', '--version'), ('clang++', '--version'), ('flang', '--version'),
                    ('python', '--version'), ('python3', '--version')]
    list_of_mpi_vendors = ['Intel', 'Open MPI']

    # Load modules
    load_modules(module_list)

    # Check list of apps
    for app, keys in list_of_apps:
        if is_available(app):
            if app == 'uname':
                output = execute_app(app, keys)
                output = output.strip()  # remove leading and trailing spaces
                info_type = 'none'
                if keys == '-o':
                    info_type = 'system'
                elif keys == '-r':
                    info_type = 'kernel version'
                elif keys == '-m':
                    info_type = 'machine'
                print(info_type + ': ' + output)
            else:
                print(app + ': found')
                output = execute_app(app, keys)
                if app == 'mpirun':
                    for vendor in list_of_mpi_vendors:
                        if vendor in output:
                            print(app + ' vendor: ' + vendor)
                print_version(app, output)
        else:
            print(app + ': not found')


def generate_batch_file(filename, module_list, exe_name, exe_options='', nodes=1, ntasks=1, cpus=1, partition='thin',
                        time=1):
    """
    Generate batch script from the provided input
    :param filename: Name of the batch script
    :param module_list: List of modules
    :param exe_name: Name of the executable file
    :param exe_options: Options for the executable file
    :param nodes: Number of nodes
    :param ntasks: Number of tasks
    :param cpus: Number of cpus
    :param partition: Partition name
    :param time: Time constraint
    :return: None
    """
    file_shebang = '#!/bin/bash'
    file_version = '#\n' \
                   '# This batch script was autogenerated by CowBerry v{0}\n' \
                   '#'.format(VERSION)
    file_header = '#SBATCH -N {0}\n' \
                  '#SBATCH -n {1}\n' \
                  '#SBATCH -c {2}\n' \
                  '#SBATCH -p {3}\n' \
                  '#SBATCH -t {4}\n'.format(nodes, ntasks, cpus,
                                            partition, time)

    file_body = '# main body is empty\n'
    file_module = 'module purge\n'
    for module in module_list:
        file_module += 'module load ' + module + '\n'

    file_cmd = 'srun ' + exe_name + ' ' + exe_options

    full_text = file_shebang + '\n' \
                + file_version + '\n' \
                + file_header + '\n' \
                + file_module + '\n' \
                + file_body + '\n' \
                + file_cmd

    print('----------------------------------------')
    print(full_text)
    print('----------------------------------------')

    # dump_to_file(filename, full_text)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    batch_script_name = 'test.sh'
    # note, the module environment should always be at the first place
    modules = ['2022', 'foss/2022a']
    print('\n--- start test')

    print('\n--- report statistics')
    report_statistics(modules)

    print('\n--- generate batch script')
    generate_batch_file('test.sh', modules, 'run.exe', '-x 100')
