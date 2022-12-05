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

            # max_rep = self.get_src_data().get_num_repetitions()
            # for rep in range(0, max_rep):
            #     io_manager.print_info('Iteration: ' + str(rep + 1) + '/' + str(max_rep))
            #
            #     # Submit job script
            #     # Change to test directory
            #     os.chdir(full_tmp_path)
            #     job_id, state = self.get_batch_data().submit_job_script(batch_file_name)
            #     # Change back to working directory
            #     os.chdir(self.get_root_dir_name())
            #
            #     # Skip failing jobs (won't be used in the report)
            #     if (job_id is not None) and (state != 'CANCELLED'):
            #         successful_jobs['id'].append(job_id)
            #         successful_jobs['dir'].append(full_tmp_path)
            #         successful_jobs['threads'].append(num_threads)

            self.report_end_of_test(counter, num_tests)

        report = GenericReport()
        report.report_parallel_results(self, self.get_src_data(), successful_jobs)
