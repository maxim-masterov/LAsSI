import os
import numpy as np
from plot import Plot

import io_manager


class Tests:
    # MPI advanced collective calls
    # key - envar
    # value - max possible value of the 'key'
    _impi_collectives = {
        'I_MPI_ADJUST_ALLREDUCE': 12,
        'I_MPI_ADJUST_BARRIER': 9,
        'I_MPI_ADJUST_BCAST': 14,
        'I_MPI_ADJUST_REDUCE': 11,
    }

    def compiler_flags(self, exec, batch_data, src_data):
        ####################
        """
        Run tests with different compiler flags
        :param exec: Object of executer
        :param batch_data: Object of batch file data
        :param src_data: Object of source data
        """
        list_wrk_dirs = []
        list_job_id = []
        counter = 0
        num_tests = len(src_data.get_compiler_flags())
        for flag_id in range(num_tests):
            counter += 1
            io_manager.print_info('[' + str(counter) + '/' + str(num_tests) + ']'
                                  + ' Starting test')
            postfix = '_flags_' + str(flag_id)

            # create temp directory with a wrorking copy of sources
            tmp_dir_name = 'run' + postfix
            exec.create_wrk_copy(src_data, tmp_dir_name)
            full_tmp_path = os.path.join(exec.get_full_wrk_dir_path(), tmp_dir_name)    
            batch_file_name = batch_data.generate_batch_file(src_data, full_tmp_path, postfix, flag_id)

            # Submit job script
            ## Change to test directory
            os.chdir(full_tmp_path)
            job_id = batch_data.submit_batch_script(batch_file_name)
            ## Change back to working directory
            os.chdir(exec.get_root_dir_name())

            # Skip failing jobs (won't be used in the report)
            if list_job_id != None:
                list_job_id.append(job_id)
                list_wrk_dirs.append(full_tmp_path)

            io_manager.print_info('[' + str(counter) + '/' + str(num_tests) + ']'
                                  + ' Done')

        # list_wrk_dirs = ['/home/maximm/pragma/CowBerry/wrk/run_flags_0',
        #                  '/home/maximm/pragma/CowBerry/wrk/run_flags_1',
        #                  '/home/maximm/pragma/CowBerry/wrk/run_flags_2',
        #                  '/home/maximm/pragma/CowBerry/wrk/run_flags_3',
        #                  '/home/maximm/pragma/CowBerry/wrk/run_flags_4',
        #                  '/home/maximm/pragma/CowBerry/wrk/run_flags_5',
        #                  '/home/maximm/pragma/CowBerry/wrk/run_flags_6',
        #                  '/home/maximm/pragma/CowBerry/wrk/run_flags_7',
        #                  '/home/maximm/pragma/CowBerry/wrk/run_flags_8',
        #                  '/home/maximm/pragma/CowBerry/wrk/run_flags_9',
        #                  '/home/maximm/pragma/CowBerry/wrk/run_flags_10',
        #                  '/home/maximm/pragma/CowBerry/wrk/run_flags_11',
        #                  '/home/maximm/pragma/CowBerry/wrk/run_flags_12',
        #                  '/home/maximm/pragma/CowBerry/wrk/run_flags_13']
        # list_job_id = ['1855911', 
        #                '1855916',
        #                '1855921',
        #                '1855922',
        #                '1855929',
        #                '1855961',
        #                '1855963',
        #                '1855977',
        #                '1855984',
        #                '1855999',
        #                '1856004',
        #                '1856005',
        #                '1856018',
        #                '1856020']
        self._report_flags_results(exec, src_data, list_wrk_dirs, list_job_id, src_data.get_compiler_flags())

    def omp_scalability(self, exec, batch_data, src_data, thread_range):
        """
        Run tests with OpenMP
        :param exec: Object of executer
        :param batch_data: Object of batch file data
        :param src_data: Object of source data
        :param thread_range: Range of threads, excluding the last number
        """
        list_wrk_dirs = []
        list_job_id = []
        counter = 0
        num_tests = (thread_range.stop - thread_range.start) / thread_range.step
        for num_threads in thread_range:
            counter += 1
            io_manager.print_info('[' + str(counter) + '/' + str(num_tests) + ']'
                                  + ' Starting test')

            postfix = '_omp_' + str(num_threads)

            # create temp directory with a wrorking copy of sources
            tmp_dir_name = 'run' + postfix
            exec.create_wrk_copy(src_data, tmp_dir_name)
            full_tmp_path = os.path.join(exec.get_full_wrk_dir_path(), tmp_dir_name)

            batch_data.envars = [('OMP_NUM_THREADS', num_threads)]
            batch_data.cpus = num_threads
            batch_file_name = batch_data.generate_batch_file(src_data, full_tmp_path, postfix)
            # cmd, bash_file_name = batch_data.generate_interactive_cmd(src_data, postfix)
            # batch_data.submit_interactively(cmd, bash_file_name)

            # Submit job script
            ## Change to test directory
            os.chdir(full_tmp_path)
            job_id = batch_data.submit_batch_script(batch_file_name)
            ## Change back to working directory
            os.chdir(exec.get_root_dir_name())

            # Skip failing jobs (won't be used in the report)
            if list_job_id != None:
                list_job_id.append(job_id)
                list_wrk_dirs.append(full_tmp_path)

            io_manager.print_info('[' + str(counter) + '/' + str(num_tests) + ']'
                                  + ' Done')

        threads = np.arange(thread_range.start, thread_range.stop, step=thread_range.step)
        self._report_parallel_results(exec, src_data, list_wrk_dirs, list_job_id, threads)

    def _report_flags_results(self, exec, src_data, list_wrk_dirs, list_job_id, labels):
        io_manager.print_dbg_info('Parsing results')
        res = []
        for wrk_dir, job_id in zip(list_wrk_dirs, list_job_id):
            output_file = 'slurm-' + str(job_id) + '.out'
            output_file_full_path = os.path.join(wrk_dir, output_file)
            # print(output_file_full_path)
            res.append(exec.parse_output_for_perf(output_file_full_path,
                                                  src_data.get_perf_regex())[0][0])

        io_manager.print_dbg_info('Plotting results')
        pl = Plot()
        pl.plot_compiler_flags(res, labels, 'compiler_flags')

    def _report_parallel_results(self, exec, src_data, list_wrk_dirs, list_job_id, test_range):
        io_manager.print_dbg_info('Parsing results')
        res = []
        for wrk_dir, job_id in zip(list_wrk_dirs, list_job_id):
            output_file = 'slurm-' + str(job_id) + '.out'
            output_file_full_path = os.path.join(wrk_dir, output_file)
            # print(output_file_full_path)
            res.append(exec.parse_output_for_perf(output_file_full_path,
                                                  src_data.get_perf_regex())[0][0])

        io_manager.print_dbg_info('Plotting results')
        pl = Plot()
        pl.plot_scalability(res, test_range, 'scalability')
        pl.plot_parallel_efficiency(res, test_range, 'efficiency', y_label='efficiency')
