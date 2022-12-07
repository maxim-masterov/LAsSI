import io_manager
from analysis.generic_analysis import GenericAnalysis


class OMPAnalysis(GenericAnalysis):
    """
    Class of OMP-based tests
    """

    def modify_omp_envar(self, step, num_cores = 0):
        if step == 'set':
            self.get_batch_data().get_envars().append(('OMP_NUM_THREADS', num_cores))
            self.get_batch_data().set_cpus(num_cores)
        elif step == 'remove':
            self.get_batch_data().get_envars().pop()
        else:
            io_manager.print_err_info('Unrecognized step name. Use \'set\' or \'remove\' keywords')

    def run_scalability(self):
        self.scalability(self.get_src_data().get_threads_list(),
                         self.get_src_data().get_type(),
                         self.modify_omp_envar)
