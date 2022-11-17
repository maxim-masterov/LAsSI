import os


class Tests:
    def omp_scalability(self, batch_data, src_data, thread_range):
        """
        Run tests with OpenMP
        :param batch_data: Object of batch file data
        :param thread_range: Range of threads, excluding the last number
        """
        for num_threads in thread_range:
            batch_data.envars = [('OMP_NUM_THREADS', num_threads)]
            batch_data.cpus = num_threads
            postfix = '_omp_' + str(num_threads)
            # batch_file_name = batch_data.generate_batch_file(src_data, postfix)
            cmd, bash_file_name = batch_data.generate_interactive_cmd(src_data, postfix)
            batch_data.submit_interactively(cmd, bash_file_name)
            
            # batch_data.submit_batch_script(batch_file_name)
