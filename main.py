import os
import subprocess
from shutil import which
import re
import json

from batch_data import BatchData

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


def dump_text_to_file(filename, text):
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


def execute_app(app_name, app_keys, stderr=subprocess.DEVNULL):
    """
    Execute application with provided keys
    :param app_name: Name of the application
    :param app_keys: String of keys
    :param stderr: Redirect stderr to a specific stream
    :return: Stdout after execution
    """
    result = subprocess.run([app_name, app_keys], stdout=subprocess.PIPE,
                            stderr=stderr)
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
                    ('python', '--version'), ('python2', '--version'), ('python3', '--version')]
    list_of_mpi_vendors = ['Intel', 'Open MPI']

    # Load modules
    # load_modules(module_list)

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
                if app == 'python2':
                    # Python2 outputs `--version` to stderr, see 
                    # https://bugs.python.org/issue18338. We need 
                    # a separate treatment to handle this bug.
                    output = execute_app(app, keys, subprocess.STDOUT)
                else:
                    output = execute_app(app, keys)
                if app == 'mpirun':
                    for vendor in list_of_mpi_vendors:
                        if vendor in output:
                            print(app + ' vendor: ' + vendor)
                print_version(app, output)
        else:
            print(app + ': not found')

    # result = subprocess.check_output('module --version', shell=True)
    # result = subprocess.Popen(['module', '--version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # print(result.stdout.decode('utf-8'))
    # os.system('echo "module --version" > ' + tty_dev)


def generate_batch_file(batch_data):
    """
    Generate batch script from the provided input
    :param batch_data: Map of batch file data
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
                  '#SBATCH -t {4}\n'.format(batch_data.nodes, batch_data.ntasks, 
                                            batch_data.cpus, batch_data.partition,
                                            batch_data.time)

    file_body = ''
    if not batch_data.envars:
        file_body = '# main body is empty\n'
    else:
        for envar, value in batch_data.envars:
            file_body += 'export ' + envar + '=' + str(value) + '\n'

    file_module = 'module purge\n'
    for module in batch_data.modules:
        file_module += 'module load ' + module + '\n'

    file_cmd = batch_data.launcher + ' ' + batch_data.exec_name + ' ' + batch_data.exec_options

    full_text = file_shebang + '\n' \
                + file_version + '\n' \
                + file_header + '\n' \
                + file_module + '\n' \
                + file_body + '\n' \
                + file_cmd

    print('----------------------------------------')
    print(full_text)
    print('----------------------------------------')

    dump_text_to_file(batch_data.batch_script_name, full_text)


def test_omp_scalability(batch_data, thread_range):
    """
    Run tests with OpenMP
    :param batch_data: Map of batch file data
    :param thread_range: Range of threads, excluding the last number
    """
    for num_threads in thread_range:
        batch_data.envars = [('OMP_NUM_THREADS', num_threads)]
        batch_data.cpus = num_threads
        generate_batch_file(batch_data)


def read_config(batch_data, thread_range, config_file_name):
    f = open(config_file_name)
    data = json.load(f)
    batch_data.modules = data['modules']
    batch_data.exec_name = data['batch_data']['executable_name']
    batch_data.exec_options = data['batch_data']['executable_options']
    batch_data.launcher = data['batch_data']['launcher']

    thread_range = range(
        data['test_setup']['thread_range'][0],
        data['test_setup']['thread_range'][1]
    )
    f.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # note, the module environment should always be at the first place
    batch = BatchData()
    batch.batch_script_name = 'test.sh'
    # batch.exec_name = 'run.exe'
    # batch.exec_options = '-x 100'
    # batch.modules = ['2022', 'foss/2022a']
    thread_range = range(1, 3)

    # Read basic configuration
    read_config(batch, thread_range, 'config.json')

    print('\n--- start test')

    print('\n--- report statistics')
    report_statistics(batch)

    print('\n--- generate batch script')
    generate_batch_file(batch)

    test_omp_scalability(batch, thread_range)
