import os

import io_manager
from executor import Executor
from report.generic_report import GenericReport


class CompilerAnalysis(Executor):
    """
    Class of compiler-based tests
    """
    def run_flags(self):
        """
        Run tests with different compiler flags
        """
        counter = 0
        num_tests = len(self.get_src_data().get_compiler_flags())
        successful_jobs = {
            'id': [],
            'dir': [],
            'flags': [],
        }

        for flag_id in range(num_tests):
            counter += 1
            self.report_start_of_test(counter, num_tests)

            postfix = self.asemble_postfix('flags', flag_id)

            # create temp directory with a working copy of sources
            tmp_dir_name = 'run' + postfix
            self.create_wrk_copy(self.get_src_data(), tmp_dir_name)
            full_tmp_path = os.path.join(self.get_full_wrk_dir_path(), tmp_dir_name)
            batch_file_name = self.get_batch_data().generate_job_script(self.get_src_data(), full_tmp_path,
                                                                        postfix, flag_id)

            # Repeat tests a given number of times
            self.run_repetitive_tests(batch_file_name, full_tmp_path,
                                      self._src_data.get_compiler_flags()[flag_id],
                                      successful_jobs['id'], successful_jobs['dir'], successful_jobs['flags'])

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
            #         # list_job_id.append(job_id)
            #         # list_wrk_dirs.append(full_tmp_path)
            #         successful_jobs['id'].append(job_id)
            #         successful_jobs['dir'].append(full_tmp_path)
            #         successful_jobs['flags'].append(self._src_data.get_compiler_flags()[flag_id])

            self.report_end_of_test(counter, num_tests)

        report = GenericReport()
        report.report_flags_results(self, self.get_src_data(), successful_jobs, successful_jobs['flags'])
