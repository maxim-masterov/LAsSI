import os
from collections import defaultdict

from plot import Plot
import io_manager


class GenericReport:
    def _parse_results(self, exc, src_data, list_job_id, list_wrk_dirs, list_tests):
        """
        Parse output files and grep performance values
        :param exc: Object of Executor
        :param src_data: Object of SrcData
        :param list_job_id: List of jobs IDs
        :param list_wrk_dirs: List of working directories
        :param list_tests: List of test cases (e.g. names, or corresponding values)
        :return: List of found performance values
        """
        io_manager.print_dbg_info('Parsing results')
        res = []

        performance = []
        test_cases = []

        for wrk_dir, job_id, test in zip(list_wrk_dirs, list_job_id, list_tests):
            output_file = 'slurm-' + str(job_id) + '.out'
            output_file_full_path = os.path.join(wrk_dir, output_file)
            extracted_data = exc.parse_output_for_perf(output_file_full_path,
                                                       src_data.get_perf_regex())
            if not extracted_data:
                io_manager.print_err_info('Parser returned an empty list. Script will be terminated.')
                exit(1)
            performance.append(extracted_data[0])
            test_cases.append(test)

        res, cases = self._average_results(performance, test_cases)

        return res, cases

    def _average_results(self, performance, test_cases):
        """
        Average the performance results. Use list of repetitive test case names to perform
        the averaging
        :param performance: List of performance values
        :param test_cases: List of test cases (names or values)
        :return: List of averaged performance and a list of corresponding test cases
        """
        res = []

        # Combine two lists
        combined_lists = defaultdict(list)
        for test, perf in zip(test_cases, performance):
            combined_lists[test].append(perf)

        # Find an average performance
        for test, perf in combined_lists.items():
            res.append(sum(perf) / float(len(perf)))

        return res, [*combined_lists.keys()]

    def report_parallel_results(self, exc, src_data, successful_jobs):
        """
        Report results of parallel execution
        :param exc: Object of Executor
        :param src_data: Object of SrcData
        :param successful_jobs: Dictionary of lists from successfully executed jobs.
                                The keys should be 'id', 'dir' and 'cores'
        :return: None
        """
        res, cores = self._parse_results(exc, src_data,
                                         successful_jobs['id'],
                                         successful_jobs['dir'],
                                         successful_jobs['cores'])
        io_manager.print_dbg_info('Plotting results')
        pl = Plot()
        pl.plot_scalability(cores, res, 'scalability')
        pl.plot_parallel_efficiency(cores, res, 'efficiency', y_label='efficiency')

    def report_flags_results(self, exc, src_data, successful_jobs, labels, title='flags'):
        """
        Report results of compier flags tests
        :param exc: Object of Executor
        :param src_data: Object of SrcData
        :param successful_jobs: Dictionary of lists from successfully executed jobs.
                                The keys should be 'id', 'dir' and 'flag_id'
        :param labels: List of compiler flags
        :param title: Title of the plot and (also) the basename of the output file
        :return: None
        """
        res, unique_labels = self._parse_results(exc, src_data,
                                                 successful_jobs['id'],
                                                 successful_jobs['dir'],
                                                 labels)
        io_manager.print_dbg_info('Plotting results')
        pl = Plot()
        pl.plot_compiler_flags(res, unique_labels, title)
