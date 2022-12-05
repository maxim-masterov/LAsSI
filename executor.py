import shutil
import sys
import re
import os

import io_manager
from batch_data import BatchFileData
from src_data import SrcData
from systeminfo import SystemInfo


class Executor:
    """
    Contains all execution/test functions
    """
    _root_dir_name = os.getenv('PWD')
    _wrk_dir_name = 'wrk'
    _full_wrk_dir_path = os.path.join(_root_dir_name, _wrk_dir_name)

    _batch_data = BatchFileData()
    _src_data = SrcData()

    # MPI advanced collective calls
    # key - envar
    # value - max possible value of the 'key'
    _impi_collectives = {
        'I_MPI_ADJUST_ALLREDUCE': 12,
        'I_MPI_ADJUST_BARRIER': 9,
        'I_MPI_ADJUST_BCAST': 14,
        'I_MPI_ADJUST_REDUCE': 11,
    }

    _threads_range = None

    def get_src_data(self):
        return self._src_data

    def get_batch_data(self):
        return self._batch_data

    def get_root_dir_name(self):
        """
        :return: Root directory of the project
        """
        return self._root_dir_name

    def get_wrk_dir_name(self):
        """
        :return: Name of the working directory
        """
        return self._wrk_dir_name

    def get_full_wrk_dir_path(self):
        """
        :return: Full path to the working directory
        """
        return self._full_wrk_dir_path

    def prepare_env(self, filename):
        """
        Read basic configuration from the configuration file and
        set up the environment for tests. This function should be
        called prior to any test.
        :param filename: Name of the configuration file
        :return: None
        """
        # Read basic configuration
        self._batch_data.read_config(filename)
        self._src_data.read_config(filename)
        self.create_wrk_dir()

    def report_system_info(self):
        """
        Report system information. This is a secondary/debug function. It only
        reports system info and doesn't influence the execution of the tests.
        :return: None
        """
        sys_info = SystemInfo()
        sys_info.report_all(self._batch_data.get_modules())

    def create_wrk_dir(self):
        """
        Create working directory
        :return: None
        """
        self._create_dir(self.get_full_wrk_dir_path())

    def create_wrk_copy(self, src_data, dir_name):
        """
        Make a working copy of the source code
        :return: None
        """
        if src_data.get_recompile_flag():
            self._copy_src(src_data, dir_name)
        else:
            self._copy_bin(src_data, dir_name)

    def parse_output_for_perf(self, filename, regex):
        """
        Parse file 'filename' and find all values that correspond to the 
        'regex'
        :param filename: Name of the file to parse
        :param regex: Regular expression to look for in the file
        :return: List of found values
        """
        file = open(filename, 'r')
        file_content = file.read()
        file.close()

        # parse using regex
        srch = re.compile(regex)
        res = srch.findall(file_content)

        # extract all numbers
        numbers = []
        for elt in res:
            # check for numbers written in different formats
            float_int_num = r'\d+'
            float_dec_num = r'(\d+\.\d*|\d*\.\d+)'
            float_sci_num = r'(\d\.?\d*[Ee][+\-]?\d+'
            full_regex = '-?' + float_sci_num + '|' + float_dec_num + '|' + float_int_num + ')'
            number = float(re.search(full_regex, elt).group(0))
            numbers.append(number)
        
        print(filename, numbers)
        return numbers

    def _copy_tree(self, src, dst, symlinks=False, ignore=None):
        """
        Copy files recursively
        :param src: Copy from
        :param dst: Copy to
        :param symlinks: Include symlinks
        :param ignore: File to ignore
        :return: None
        """
        if os.path.exists(src):
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, symlinks, ignore)
                else:
                    shutil.copy2(s, d)
        else:
            io_manager.print_err_info('The source directory does not exist: ' + src)
            sys.exit(1)

    def _copy_src(self, src_data, dir_name):
        """
        Copy source files
        :param src_data: Object of ScrData
        :param dir_name: Path to source files
        :return: None
        """
        src_full_path = src_data.get_src_path()
        dst_full_path = os.path.join(self.get_full_wrk_dir_path(), dir_name)
        io_manager.print_dbg_info('Copy source files to the working directory: '
                                  + src_full_path + ' --> ' + dst_full_path)
        self._create_dir(dst_full_path)
        self._copy_tree(src_full_path, dst_full_path)

    def _copy_bin(self, src_data, dir_name):
        """
        Copy binary file
        :param src_data: Object of ScrData
        :param dir_name: Path to the binary file
        :return: None
        """
        src_full_path = os.path.join(src_data.get_src_path())
        dst_full_path = os.path.join(self.get_full_wrk_dir_path(), dir_name)
        io_manager.print_dbg_info('Copy a binary file to the working directory: '
                                  + src_full_path + ' --> ' + dst_full_path)
        self._create_dir(dst_full_path)
        src_full_path = os.path.join(src_full_path, src_data.get_exec_name())
        dst_full_path = os.path.join(dst_full_path, src_data.get_exec_name())
        if src_data.check_if_exec_exists():
            shutil.copy2(src_full_path, dst_full_path)

    def _create_dir(self, dir_name):
        """
        Create directory
        :param dir_name: Name of the directory to be created
        :return: None
        """
        full_path = os.path.join(self.get_root_dir_name(), dir_name)
        if not os.path.exists(full_path):
            io_manager.print_dbg_info('Creating directory: ' + full_path)
            os.mkdir(full_path)
        else:
            io_manager.print_dbg_info('Directory already exists: ' + full_path)

    def run_repetitive_tests(self, batch_file_name, full_path_wrk_dir, test_case,
                             successful_jobs_id, successful_jobs_dir, successful_jobs_test_case):
        """
        Repeat tests a given number of times
        :param batch_file_name: Name of the job script
        :param full_path_wrk_dir: Full path to the working directory
        :param test_case: Name of the test case (e.g. number of threads)
        :param successful_jobs_id: List of successful jobs IDs (in/out)
        :param successful_jobs_dir: List of successful job working directories (in/out)
        :param successful_jobs_test_case: st of successful test case names (in/out)
        :return: None
        """

        max_rep = self.get_src_data().get_num_repetitions()
        for rep in range(0, max_rep):
            io_manager.print_info('Iteration: ' + str(rep + 1) + '/' + str(max_rep))

            # Submit job script
            # Change to test directory
            os.chdir(full_path_wrk_dir)
            job_id, state = self.get_batch_data().submit_job_script(batch_file_name)
            # Change back to working directory
            os.chdir(self.get_root_dir_name())

            # Skip failing jobs (won't be used in the report)
            if (job_id is not None) and (state != 'CANCELLED'):
                successful_jobs_id.append(job_id)
                successful_jobs_dir.append(full_path_wrk_dir)
                successful_jobs_test_case.append(test_case)

    def report_start_of_test(self, counter, num_tests):
        io_manager.print_info('['
                              + str(counter) + '/'
                              + str(num_tests)
                              + '] Starting test')

    def report_end_of_test(self, counter, num_tests):
        io_manager.print_info('[' + str(counter) + '/' + str(num_tests) + ']'
                              + ' Done')

    def asemble_postfix(self, key, value):
        return '_' + str(key) + '_' + str(value)
