import os
import numpy as np
from plot import Plot

import io_manager


class Tests:
    def compiler_flags(self, exec, batch_data, src_data):
        pass
        ####################
        """
        Run tests with different compiler flags
        :param exec: Object of executer
        :param batch_data: Object of batch file data
        :param src_data: Object of source data
        """
        list_wrk_dirs = []
        list_job_id = []
        for flag_id in range(len(src_data.get_compiler_flags())):
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

            list_job_id.append(job_id)
            list_wrk_dirs.append(full_tmp_path)

        # list_wrk_dirs = [('/home/maximm/pragma/CowBerry/wrk/run_omp_1', 'slurm-1852858.out'),
        #                  ('/home/maximm/pragma/CowBerry/wrk/run_omp_2', 'slurm-1852860.out')]
        # list_wrk_dirs = ['/home/maximm/pragma/CowBerry/wrk/run_flags_0',
        #                  '/home/maximm/pragma/CowBerry/wrk/run_flags_1']
        # list_job_id = ['1854728', '1854731']
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
        for num_threads in thread_range:
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

            list_job_id.append(job_id)
            list_wrk_dirs.append(full_tmp_path)

        # list_wrk_dirs = [('/home/maximm/pragma/CowBerry/wrk/run_omp_1', 'slurm-1852858.out'),
        #                  ('/home/maximm/pragma/CowBerry/wrk/run_omp_2', 'slurm-1852860.out')]
        # list_wrk_dirs = ['/home/maximm/pragma/CowBerry/wrk/run_omp_1',
        #                  '/home/maximm/pragma/CowBerry/wrk/run_omp_2']
        # list_job_id = ['1853463', '1853464']
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
