import os

from executor import Executor
from report.generic_report import GenericReport


class GenericAnalysis(Executor):
    """
    Class of generic tests
    """

    def scalability(self, cores_list, test_name, modify_batch_script=None):
        """
        Generic scalability test
        :param cores_list: List of cores/threads
        :param test_name: Name of the test, e.g. 'omp'
        :param modify_envars: Function pointer to set environmnet variables before
                           the batch file is generated. The function should have:
                           - one mandatory string argument that will indicate if
                           an environment variable should be set ('set') or removed
                           ('remove') from the internal list of envars
                           - one optional integer argumetn that indicates the current
                           test case number
        """
        counter = 0
        num_tests = len(cores_list)
        successful_jobs = {
            'id': [],
            'dir': [],
            'cores': [],
        }

        for num_cores in cores_list:
            counter += 1
            self.report_start_of_test(counter, num_tests)
            self.report_test_info(test_name, num_cores)

            postfix = self.asemble_postfix(test_name, num_cores)

            # create temp directory with a working copy of sources
            tmp_dir_name = 'run' + postfix
            self.create_wrk_copy(self.get_src_data(), tmp_dir_name)
            full_tmp_path = os.path.join(self.get_full_wrk_dir_path(), tmp_dir_name)

            # append and then pop a new envar to the list of already existing envars
            if modify_batch_script is not None:
                modify_batch_script('set', num_cores)

            batch_file_name = self.get_batch_data().generate_job_script(self.get_src_data(), full_tmp_path,
                                                                        postfix)

            if modify_batch_script is not None:
                modify_batch_script('remove', num_cores)

            # Repeat tests a given number of times
            self.run_repetitive_tests(batch_file_name, full_tmp_path, num_cores,
                                      successful_jobs['id'], successful_jobs['dir'], successful_jobs['cores'])

            self.report_end_of_test(counter, num_tests)

        report = GenericReport()
        report.report_parallel_results(self, self.get_src_data(), successful_jobs)
