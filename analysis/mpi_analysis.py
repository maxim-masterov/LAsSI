import os
import math

import io_manager
from report.generic_report import GenericReport
from analysis.generic_analysis import GenericAnalysis


class MPIAnalysis(GenericAnalysis):
    """
    Class of MPI-based tests
    """

    # IMPI advanced collective calls
    # key - envar
    # value - max possible value of the 'key'
    _impi_collectives = {
        'I_MPI_ADJUST_ALLREDUCE': 12,
        'I_MPI_ADJUST_BARRIER': 9,
        'I_MPI_ADJUST_BCAST': 14,
        'I_MPI_ADJUST_REDUCE': 11,
    }

    # OpenMPI advanced collective calls
    # key - mca parameter
    # value - max possible value of the 'key' (starts from 0)
    _ompi_collectives = {
        'coll_tuned_allreduce_algorithm': 6,
        'coll_tuned_barrier_algorithm': 9,
        'coll_tuned_bcast_algorithm': 6,
        'coll_tuned_reduce_algorithm': 7,
    }

    def get_impi_collectives(self):
        return self._impi_collectives

    def get_ompi_collectives(self):
        return self._ompi_collectives

    def _get_num_tests(self, _mpi_coll_dict):
        num_tests = 0
        for key in _mpi_coll_dict:
            num_tests += _mpi_coll_dict[key]
        return num_tests

    def run_collectives(self):
        """
        Run tests with different compiler flags
        """
        # Define what dictionary of collectives to use based on the 'compile_command'
        # from the config file
        ompi_wrappers = ['mpiCC', 'mpic++', 'mpicc', 'mpicxx', 'mpif77', 'mpif90', 'mpifort']
        impi_wrappers = ['mpiicc', 'mpiicpc', 'mpiifort']
        mpi_coll_dict = None
        mpi_vendor = ''
        compiler_cmd = self.get_src_data().get_compiler_cmd()
        if compiler_cmd in ompi_wrappers:
            mpi_coll_dict = self.get_ompi_collectives()
            mpi_vendor = 'OpenMPI'
        elif compiler_cmd in impi_wrappers:
            mpi_coll_dict = self.get_impi_collectives()
            mpi_vendor = 'IMPI'
        else:
            io_manager.print_err_info('Cannot determine vendor of the MPI compiler wrapper: ' + str(compiler_cmd))
            exit(1)

        counter = 0
        num_tests = self._get_num_tests(mpi_coll_dict)
        successful_jobs = {
            'id': [],
            'dir': [],
            'type': [],
        }

        start_range = 1
        if mpi_vendor == 'OpenMPI':
            start_range = 0
            num_tests += len(mpi_coll_dict)

        for col_type in mpi_coll_dict:
            max_range = mpi_coll_dict[col_type] + 1
            for value in range(start_range, max_range):
                counter += 1
                self.report_start_of_test(counter, num_tests)

                test_case = col_type + '_' + str(value)
                postfix = self.asemble_postfix('col_flags', test_case)

                # create temp directory with a working copy of sources
                tmp_dir_name = 'run' + postfix
                self.create_wrk_copy(self.get_src_data(), tmp_dir_name)
                full_tmp_path = os.path.join(self.get_full_wrk_dir_path(), tmp_dir_name)

                # append and then pop a new envar to the list of already existing envars
                default_launcher = self.get_batch_data().get_launcher()
                if mpi_vendor == 'IMPI':
                    self.get_batch_data().get_envars().append((col_type, value))
                elif mpi_vendor == 'OpenMPI':
                    # Force modify the default launcher if it was set to 'srun'
                    if default_launcher == 'srun':
                        default_launcher = 'mpirun'
                    mod_launcher = default_launcher + ' --mca ' + col_type + ' ' + str(value) + ' '
                    self.get_batch_data().set_launcher(mod_launcher)
                batch_file_name = self.get_batch_data().generate_job_script(self.get_src_data(), full_tmp_path,
                                                                            postfix)
                if mpi_vendor == 'IMPI':
                    self.get_batch_data().get_envars().pop()
                elif mpi_vendor == 'OpenMPI':
                    self.get_batch_data().set_launcher(default_launcher)

                # Repeat tests a given number of times
                self.run_repetitive_tests(batch_file_name, full_tmp_path,
                                          test_case,
                                          successful_jobs['id'], 
                                          successful_jobs['dir'],
                                          successful_jobs['type'])

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
