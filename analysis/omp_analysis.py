import os

import io_manager
from executor import Executor
from report.generic_report import GenericReport


class OMPAnalysis(Executor):
    """
    Class of OMP-based tests
    """
    def run_scalability(self):
        """
        Run scalability test
        """
        counter = 0
        threads_list = self.get_src_data().get_threads_list()
        num_tests = len(threads_list)
        successful_jobs = {
            'id': [],
            'dir': [],
            'threads': [],
        }

        for num_threads in threads_list:
            counter += 1
            self.report_start_of_test(counter, num_tests)

            postfix = self.asemble_postfix('omp', num_threads)

            # create temp directory with a working copy of sources
            tmp_dir_name = 'run' + postfix
            self.create_wrk_copy(self.get_src_data(), tmp_dir_name)
            full_tmp_path = os.path.join(self.get_full_wrk_dir_path(), tmp_dir_name)

            # append and then pop a new envar to the list of already existing envars
            self.get_batch_data().get_envars().append(('OMP_NUM_THREADS', num_threads))
            self.get_batch_data().set_cpus(num_threads)
            batch_file_name = self.get_batch_data().generate_job_script(self.get_src_data(), full_tmp_path,
                                                                        postfix)
            self.get_batch_data().get_envars().pop()

            # Repeat tests a given number of times
            self.run_repetitive_tests(batch_file_name, full_tmp_path, num_threads,
                                      successful_jobs['id'], successful_jobs['dir'], successful_jobs['threads'])

            self.report_end_of_test(counter, num_tests)

        report = GenericReport()
        report.report_parallel_results(self, self.get_src_data(), successful_jobs)
