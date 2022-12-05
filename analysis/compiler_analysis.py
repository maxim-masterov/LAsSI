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

            self.report_end_of_test(counter, num_tests)

        report = GenericReport()
        report.report_flags_results(self, self.get_src_data(), successful_jobs,
                                    successful_jobs['flags'], 'compiler_flags')
