import os


class Tests:
    def omp_scalability(self, exec, batch_data, src_data, thread_range):
        """
        Run tests with OpenMP
        :param batch_data: Object of batch file data
        :param thread_range: Range of threads, excluding the last number
        """
        for num_threads in thread_range:
            postfix = '_omp_' + str(num_threads)
            
            # create temp directory with a wrorking copy of sources
            tmp_dir_name = 'run' + postfix
            exec.create_wrk_copy(src_data, tmp_dir_name)
            full_tmp_path = os.path.join(exec.get_full_wrk_dir_path(), tmp_dir_name)
            print(full_tmp_path)
            batch_data.envars = [('OMP_NUM_THREADS', num_threads)]
            batch_data.cpus = num_threads
            batch_file_name = batch_data.generate_batch_file(src_data, full_tmp_path, postfix)
            # cmd, bash_file_name = batch_data.generate_interactive_cmd(src_data, postfix)
            # batch_data.submit_interactively(cmd, bash_file_name)
            
            # Change to test directory
            os.chdir(full_tmp_path)
            batch_data.submit_batch_script(batch_file_name)
            # Change back to working directory
            os.chdir(exec.get_root_dir_name())
