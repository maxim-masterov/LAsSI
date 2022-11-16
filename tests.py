class Tests:

    def omp_scalability(self, batch_data, thread_range):
        """
        Run tests with OpenMP
        :param batch_data: Object of batch file data
        :param thread_range: Range of threads, excluding the last number
        """
        for num_threads in thread_range:
            batch_data.envars = [('OMP_NUM_THREADS', num_threads)]
            batch_data.cpus = num_threads
            postfix = '_omp_' + str(num_threads)
            batch_data.generate_batch_file(postfix)
