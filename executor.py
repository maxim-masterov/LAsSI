import shutil
import sys
import re
import os

from plot import Plot
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

    # def compiler_flags(self):
    #     """
    #     Run tests with different compiler flags
    #     :param exc: Object of the executor
    #     :param batch_data: Object of batch file data
    #     :param src_data: Object of source data
    #     """
    #     list_wrk_dirs = []
    #     list_job_id = []
    #     counter = 0
    #     num_tests = len(self._src_data.get_compiler_flags())
    #     for flag_id in range(num_tests):
    #         counter += 1
    #         io_manager.print_info('[' + str(counter) + '/' + str(num_tests) + ']'
    #                               + ' Starting test')
    #         postfix = '_flags_' + str(flag_id)
    #
    #         # create temp directory with a working copy of sources
    #         tmp_dir_name = 'run' + postfix
    #         self.create_wrk_copy(self._src_data, tmp_dir_name)
    #         full_tmp_path = os.path.join(self.get_full_wrk_dir_path(), tmp_dir_name)
    #         batch_file_name = self._batch_data.generate_job_script(self._src_data, full_tmp_path, postfix, flag_id)
    #
    #         # Submit job script
    #         # Change to test directory
    #         os.chdir(full_tmp_path)
    #         job_id = self._batch_data.submit_job_script(batch_file_name)
    #         # Change back to working directory
    #         os.chdir(self.get_root_dir_name())
    #
    #         # Skip failing jobs (won't be used in the report)
    #         if list_job_id is not None:
    #             list_job_id.append(job_id)
    #             list_wrk_dirs.append(full_tmp_path)
    #
    #         io_manager.print_info('[' + str(counter) + '/' + str(num_tests) + ']'
    #                               + ' Done')
    #
    #     # list_wrk_dirs = ['/home/maximm/pragma/CowBerry/wrk/run_flags_0',
    #     #                  '/home/maximm/pragma/CowBerry/wrk/run_flags_1']
    #     # list_job_id = ['1855911',
    #     #                '1855916']
    #     self._report_flags_results(list_wrk_dirs, list_job_id, self._src_data.get_compiler_flags())

    def omp_scalability(self):
        """
        Run tests with OpenMP
        :param exc: Object of executor
        :param batch_data: Object of batch file data
        :param src_data: Object of source data
        """
        list_wrk_dirs = []
        list_job_id = []
        counter = 0
        # threads_range = self._src_data.get_threads_range()
        # num_tests = int((threads_range.stop - threads_range.start) / threads_range.step)
        threads_list = self._src_data.get_threads_list()
        num_tests = len(threads_list)
        for num_threads in threads_list:
            counter += 1
            io_manager.print_info('[' + str(counter) + '/' + str(num_tests) + ']'
                                  + ' Starting test')

            postfix = '_omp_' + str(num_threads)

            # create temp directory with a wrorking copy of sources
            tmp_dir_name = 'run' + postfix
            self.create_wrk_copy(self._src_data, tmp_dir_name)
            full_tmp_path = os.path.join(self.get_full_wrk_dir_path(), tmp_dir_name)

            # append and then pop a new envar to the list of already existing envars
            self._batch_data.get_envars().append(('OMP_NUM_THREADS', num_threads))
            self._batch_data.set_cpus(num_threads)
            batch_file_name = self._batch_data.generate_job_script(self._src_data, full_tmp_path, postfix)
            self._batch_data.get_envars().pop()
            # cmd, bash_file_name = batch_data.generate_interactive_cmd(src_data, postfix)
            # batch_data.submit_interactively(cmd, bash_file_name)

            # Submit job script
            # Change to test directory
            os.chdir(full_tmp_path)
            job_id = self._batch_data.submit_job_script(batch_file_name)
            # Change back to working directory
            os.chdir(self.get_root_dir_name())

            # Skip failing jobs (won't be used in the report)
            if list_job_id is not None:
                list_job_id.append(job_id)
                list_wrk_dirs.append(full_tmp_path)

            io_manager.print_info('[' + str(counter) + '/' + str(num_tests) + ']'
                                  + ' Done')

        self._report_parallel_results(self._src_data, list_wrk_dirs, list_job_id, threads_list)

    # def _report_flags_results(self, list_wrk_dirs, list_job_id, labels):
    #     io_manager.print_dbg_info('Parsing results')
    #     res = []
    #     for wrk_dir, job_id in zip(list_wrk_dirs, list_job_id):
    #         output_file = 'slurm-' + str(job_id) + '.out'
    #         output_file_full_path = os.path.join(wrk_dir, output_file)
    #         # print(output_file_full_path)
    #         res.append(self.parse_output_for_perf(output_file_full_path,
    #                                                     self._src_data.get_perf_regex())[0][0])
    #
    #     io_manager.print_dbg_info('Plotting results')
    #     pl = Plot()
    #     pl.plot_compiler_flags(res, labels, 'compiler_flags')

    # def _report_parallel_results(self, src_data, list_wrk_dirs, list_job_id, test_range):
    #     io_manager.print_dbg_info('Parsing results')
    #     res = []
    #     for wrk_dir, job_id in zip(list_wrk_dirs, list_job_id):
    #         output_file = 'slurm-' + str(job_id) + '.out'
    #         output_file_full_path = os.path.join(wrk_dir, output_file)
    #         # print(output_file_full_path)
    #         res.append(self.parse_output_for_perf(output_file_full_path,
    #                                              src_data.get_perf_regex())[0])
    #
    #     io_manager.print_dbg_info('Plotting results')
    #     pl = Plot()
    #     pl.plot_scalability(test_range, res, 'scalability')
    #     pl.plot_parallel_efficiency(test_range, res, 'efficiency', y_label='efficiency')