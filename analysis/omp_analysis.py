import os

import io_manager
from analysis.generic_analysis import GenericAnalysis
from report.generic_report import GenericReport


class OMPAnalysis(GenericAnalysis):
    """
    Class of OMP-based tests
    """
    _omp_affinity = {
        'OMP_PROC_BIND': ['true', 'false', 'master', 'close', 'spread'],
        'OMP_PLACES': ['threads', 'cores', 'sockets', 'll_caches', 'numa_domains']
    }

    def get_omp_affinity(self):
        return self._omp_affinity

    def get_num_affinity_tests(self):
        num_elts = 1
        for key, value in self.get_omp_affinity().items():
            num_elts *= len(value)
        return num_elts

    def modify_omp_envar(self, step, num_cores = 0):
        if step == 'set':
            self.get_batch_data().get_envars().append(('OMP_NUM_THREADS', num_cores))
            self.get_batch_data().set_cpus(num_cores)
        elif step == 'remove':
            self.get_batch_data().get_envars().pop()
        else:
            io_manager.print_err_info('Unrecognized step name. Use \'set\' or \'remove\' keywords')

    def modify_omp_envar_affinity(self, step, num_cores = 0, bind = '', place = ''):
        if step == 'set':
            self.get_batch_data().get_envars().append(('OMP_NUM_THREADS', num_cores))
            self.get_batch_data().get_envars().append(('OMP_PROC_BIND', bind))
            self.get_batch_data().get_envars().append(('OMP_PLACES', place))
            self.get_batch_data().set_cpus(num_cores)
        elif step == 'remove':
            self.get_batch_data().get_envars().pop()
            self.get_batch_data().get_envars().pop()
            self.get_batch_data().get_envars().pop()
        else:
            io_manager.print_err_info('Unrecognized step name. Use \'set\' or \'remove\' keywords')

    def run_scalability(self):
        self.scalability(self.get_src_data().get_threads_list(),
                         self.get_src_data().get_type(),
                         self.modify_omp_envar)

    def run_affinity(self):
        cores_list = self.get_src_data().get_threads_list()
        num_tests = self.get_num_affinity_tests() * len(cores_list)
        test_name = self.get_src_data().get_type()
        modify_batch_script = self.modify_omp_envar_affinity

        io_manager.print_dbg_info('The "run_affinity" test is still in development. So, no warranty.')

        successful_jobs = []
        counter = 0
        for bind in self.get_omp_affinity()['OMP_PROC_BIND']:
            for place in self.get_omp_affinity()['OMP_PLACES']:
                ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
                # num_tests = len(cores_list)
                local_successful_jobs = {
                    'id': [],
                    'dir': [],
                    'cores': [],
                    'label': bind + '+' + place,
                }

                for num_cores in cores_list:
                    counter += 1
                    self.report_start_of_test(counter, num_tests)
                    self.report_test_info(test_name, bind + '/' + place + ' | ' + str(num_cores))

                    postfix = self.asemble_postfix(test_name, num_cores)

                    # create temp directory with a working copy of sources
                    tmp_dir_name = 'run' + postfix
                    self.create_wrk_copy(self.get_src_data(), tmp_dir_name)
                    full_tmp_path = os.path.join(self.get_full_wrk_dir_path(), tmp_dir_name)

                    # append and then pop a new envar to the list of already existing envars
                    if modify_batch_script is not None:
                        modify_batch_script('set', num_cores, bind, place)

                    batch_file_name = self.get_batch_data().generate_job_script(self.get_src_data(), full_tmp_path,
                                                                                postfix)

                    if modify_batch_script is not None:
                        modify_batch_script('remove', num_cores, bind, place)

                    # Repeat tests a given number of times
                    self.run_repetitive_tests(batch_file_name, full_tmp_path, num_cores,
                                              local_successful_jobs['id'], 
                                              local_successful_jobs['dir'],
                                              local_successful_jobs['cores'])

                    self.report_end_of_test(counter, num_tests)

                successful_jobs.append(local_successful_jobs)

        report = GenericReport()
        report.report_parallel_results(self, self.get_src_data(), successful_jobs)
