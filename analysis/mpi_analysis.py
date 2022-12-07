import os
import math

import io_manager
from report.generic_report import GenericReport
from analysis.generic_analysis import GenericAnalysis


class MPIAnalysis(GenericAnalysis):
    """
    Class of MPI-based tests
    """

    # MPI advanced collective calls
    # key - envar
    # value - max possible value of the 'key'
    _impi_collectives = {
        'I_MPI_ADJUST_ALLREDUCE': 12,
        'I_MPI_ADJUST_BARRIER': 9,
        'I_MPI_ADJUST_BCAST': 14,
        'I_MPI_ADJUST_REDUCE': 11,
    }

    def get_impi_collectives(self):
        return self._impi_collectives

    def _get_num_tests(self):
        num_tests = 0
        for key in self.get_impi_collectives():
            num_tests += self.get_impi_collectives()[key]
        return num_tests

    def run_collectives(self):
        """
        Run tests with different compiler flags
        """
        counter = 0
        num_tests = self._get_num_tests()
        successful_jobs = {
            'id': [],
            'dir': [],
            'type': [],
        }

        for col_type in self.get_impi_collectives():
            max_range = self.get_impi_collectives()[col_type] + 1
            for value in range(1, max_range):
                counter += 1
                self.report_start_of_test(counter, num_tests)

                test_case = col_type + '_' + str(value)
                postfix = self.asemble_postfix('col_flags', test_case)

                # create temp directory with a working copy of sources
                tmp_dir_name = 'run' + postfix
                self.create_wrk_copy(self.get_src_data(), tmp_dir_name)
                full_tmp_path = os.path.join(self.get_full_wrk_dir_path(), tmp_dir_name)

                # append and then pop a new envar to the list of already existing envars
                self.get_batch_data().get_envars().append((col_type, value))
                batch_file_name = self.get_batch_data().generate_job_script(self.get_src_data(), full_tmp_path,
                                                                            postfix)
                self.get_batch_data().get_envars().pop()

                # Repeat tests a given number of times
                self.run_repetitive_tests(batch_file_name, full_tmp_path,
                                          test_case,
                                          successful_jobs['id'], successful_jobs['dir'], successful_jobs['type'])

                self.report_end_of_test(counter, num_tests)

        report = GenericReport()
        report.report_flags_results(self, self.get_src_data(), successful_jobs,
                                    successful_jobs['type'], 'collective_calls')

    def modify_ntasks(self, step, num_cores=0):
        if step == 'set':
            max_tasks_per_node = self.get_batch_data().get_max_cores_pre_node()
            nodes = int(math.ceil(num_cores / max_tasks_per_node))
            self.get_batch_data().set_nodes(nodes)
            self.get_batch_data().set_ntasks(num_cores)
        elif step == 'remove':
            pass
        else:
            io_manager.print_err_info('Unrecognized step name. Use \'set\' or \'remove\' keywords')

    def run_scalability(self):
        self.scalability(self.get_src_data().get_tasks_list(),
                         self.get_src_data().get_type(),
                         self.modify_ntasks)
