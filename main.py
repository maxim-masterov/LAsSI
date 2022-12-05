from analysis.omp_analysis import OMPAnalysis
from analysis.compiler_analysis import CompilerAnalysis
from analysis.mpi_analysis import MPIAnalysis

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # test = CompilerAnalysis()
    # test = OMPAnalysis()
    test = MPIAnalysis()

    # Prepare the test environment
    test.prepare_env('config.json')

    # Report some information about the system
    test.report_system_info()

    # Execute tests
    # test.run_scalability()
    # test.run_flags()
    test.run_collectives()
