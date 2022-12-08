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
    all_known_cases = ['compiler_flags',
                       'omp_scalability',
                       'mpi_scalability', 'mpi_collective']
    case_found = False

    for known_case in all_known_cases:
        if case_name == known_case:
            case_found = True
            if 'omp_' in case_name:
                test = OMPAnalysis()
                test.prepare_env(config_file_name)
                test.report_system_info()
                test.run_scalability()
            elif 'mpi_' in case_name:
                test = MPIAnalysis()
                test.prepare_env(config_file_name)
                test.report_system_info()
                if '_scalability' in case_name:
                    test.run_scalability()
                if '_collective' in case_name:
                    test.run_collectives()
            elif 'compiler_' in case_name:
                test = CompilerAnalysis()
                test.prepare_env(config_file_name)  # Prepare the test environment
                test.report_system_info()           # Report some information about the system
                test.run_flags()                    # Execute tests

    if not case_found:
        io_manager.print_err_info('The test case \'' + str(case_name) + '\' is not found '
                                  'in the list of known test case names: ', all_known_cases)
        exit(1)
