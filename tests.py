import os
import numpy as np
from plot import Plot


class Tests:
    def omp_scalability(self, exec, batch_data, src_data, thread_range):
        """
        Run tests with OpenMP
        :param batch_data: Object of batch file data
        :param thread_range: Range of threads, excluding the last number
        """
        # list_wrk_dirs = []
        # for num_threads in thread_range:
        #     postfix = '_omp_' + str(num_threads)
            
        #     # create temp directory with a wrorking copy of sources
        #     tmp_dir_name = 'run' + postfix
        #     exec.create_wrk_copy(src_data, tmp_dir_name)
        #     full_tmp_path = os.path.join(exec.get_full_wrk_dir_path(), tmp_dir_name)
            
        #     batch_data.envars = [('OMP_NUM_THREADS', num_threads)]
        #     batch_data.cpus = num_threads
        #     batch_file_name = batch_data.generate_batch_file(src_data, full_tmp_path, postfix)
        #     # cmd, bash_file_name = batch_data.generate_interactive_cmd(src_data, postfix)
        #     # batch_data.submit_interactively(cmd, bash_file_name)
            
        #     # Submit job script
        #     ## Change to test directory
        #     os.chdir(full_tmp_path)
        #     batch_data.submit_batch_script(batch_file_name)
        #     ## Change back to working directory
        #     os.chdir(exec.get_root_dir_name())

        #     list_wrk_dirs.append(full_tmp_path)

        list_wrk_dirs = [('/home/maximm/pragma/CowBerry/wrk/run_omp_1', 'slurm-1852858.out'),
                         ('/home/maximm/pragma/CowBerry/wrk/run_omp_2', 'slurm-1852860.out')]

        res = []
        for wrk_dir, output_file in list_wrk_dirs:
            print(wrk_dir)
            output_file_full_path = os.path.join(wrk_dir, output_file)
            res.append(exec.parse_output_for_perf(output_file_full_path,src_data.get_perf_regex())[0][0])
        threads = np.arange(1, len(res) + 1, step=1)
        print(res)
        print(threads)

        pl = Plot()
        pl.plot_scalability(res, threads, 'scalability')
        pl.plot_parallel_efficiency(res, threads, 'efficiency', y_label='efficiency')
