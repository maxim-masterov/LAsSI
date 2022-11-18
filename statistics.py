from shutil import which
import subprocess
import re

import io_manager


class Statistics:
    def get_version_from_text(self, text):
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

    def print_version(self, app_name, text):
        """
        Simply reports a version name of the 'app' to the console
        :param app_name: Application name
        :param text: Text that has a version name in it
        :return: None
        """
        io_manager.print_info(app_name + ' version: ' + self.get_version_from_text(text))

    def is_available(self, app_name):
        """
        Check whether program `name` exists in a PATH or not
        :param app_name: Application name
        :return: True if app exists, false otherwise
        """
        return which(app_name) is not None

    def execute_app(self, app_name, app_keys, stderr=subprocess.DEVNULL):
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

    def report_statistics(self, module_list):
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
            if self.is_available(app):
                if app == 'uname':
                    output = self.execute_app(app, keys)
                    output = output.strip()  # remove leading and trailing spaces
                    info_type = 'none'
                    if keys == '-o':
                        info_type = 'system'
                    elif keys == '-r':
                        info_type = 'kernel version'
                    elif keys == '-m':
                        info_type = 'machine'
                    io_manager.print_info(info_type + ': ' + output)
                else:
                    io_manager.print_info(app + ': found')
                    if app == 'python2':
                        # Python2 outputs `--version` to stderr, see
                        # https://bugs.python.org/issue18338. We need
                        # a separate treatment to handle this bug.
                        output = self.execute_app(app, keys, subprocess.STDOUT)
                    else:
                        output = self.execute_app(app, keys)
                    if app == 'mpirun':
                        for vendor in list_of_mpi_vendors:
                            if vendor in output:
                                io_manager.print_info(app + ' vendor: ' + vendor)
                    self.print_version(app, output)
            else:
                io_manager.print_info(app + ': not found')

    def load_modules(self, module_list):
        # Load modules
        if len(self.module_list) > 0:
            if self.is_available('module'):
                subprocess.run(['module', 'purge'])
                for module in module_list:
                    subprocess.run(['module', 'load', module])

            else:
                io_manager.print_err_info('A module list was specified but there is '
                                          'no \'module\' command available')