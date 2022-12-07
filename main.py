import json

import io_manager
from analysis.omp_analysis import OMPAnalysis
from analysis.compiler_analysis import CompilerAnalysis
from analysis.mpi_analysis import MPIAnalysis


def detect_test_case(_config_file_name):
    f = open(_config_file_name)
    data = json.load(f)
    _case_name = data['test_setup']['type']
    f.close()
    return _case_name


if __name__ == '__main__':

    config_file_name = 'config.json'
    case_name = detect_test_case(config_file_name)

    if case_name == 'compiler_flags':
        test = CompilerAnalysis()
        test.prepare_env(config_file_name)  # Prepare the test environment
        test.report_system_info()           # Report some information about the system
        test.run_flags()                    # Execute tests
    elif case_name == 'omp':
        test = OMPAnalysis()
        test.prepare_env(config_file_name)
        test.report_system_info()
        test.run_scalability()
    elif case_name == 'mpi_scalability':
        test = MPIAnalysis()
        test.prepare_env(config_file_name)
        test.report_system_info()
        test.run_scalability()
    elif case_name == 'mpi_collective':
        test = MPIAnalysis()
        test.prepare_env(config_file_name)
        test.report_system_info()
        test.run_collectives()
    else:
        io_manager.print_err_info('Unknown test case name.')
        exit(1)
