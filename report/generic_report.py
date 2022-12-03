import os

from plot import Plot
import io_manager


class GenericReport:
    def _parse_results(self, exc, src_data, list_wrk_dirs, list_job_id):
        """
        Parse output files and grep performance values
        :param exc: Object of Executor
        :param src_data: Object of SrcData
        :param list_wrk_dirs: List of working directories
        :param list_job_id: List of jobs IDs
        :return: List of found performance values
        """
        io_manager.print_dbg_info('Parsing results')
        res = []
        for wrk_dir, job_id in zip(list_wrk_dirs, list_job_id):
            output_file = 'slurm-' + str(job_id) + '.out'
            output_file_full_path = os.path.join(wrk_dir, output_file)
            res.append(exc.parse_output_for_perf(output_file_full_path,
                                                 src_data.get_perf_regex())[0])
        return res

    def report_parallel_results(self, exc, src_data, successful_jobs):
        """
        Report results of parallel execution
        :param exc: Object of Executor
        :param src_data: Object of SrcData
        :param successful_jobs: Dictionary of lists from successfully executed jobs.
                                The keys should be 'threads', 'id', 'dir'
        :return: None
        """
        res = self._parse_results(exc, src_data, successful_jobs['dir'], successful_jobs['id'])
        io_manager.print_dbg_info('Plotting results')
        pl = Plot()
        pl.plot_scalability(successful_jobs['threads'], res, 'scalability')
        pl.plot_parallel_efficiency(successful_jobs['threads'], res, 'efficiency', y_label='efficiency')

    def report_flags_results(self, exc, src_data, successful_jobs, labels):
        """
        Report results of compier flags tests
        :param exc: Object of Executor
        :param src_data: Object of SrcData
        :param successful_jobs: Dictionary of lists from successfully executed jobs.
                                The keys should be 'threads', 'id', 'dir'
        :param labels: List of compiler flags
        :return: None
        """
        res = self._parse_results(exc, src_data, successful_jobs['dir'], successful_jobs['id'])
        io_manager.print_dbg_info('Plotting results')
        pl = Plot()
        pl.plot_compiler_flags(res, labels, 'compiler_flags')