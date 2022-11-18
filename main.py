from batch_data import BatchFileData
from src_data import SrcData
from tests import Tests
from executer import Executer
from statistics import Statistics


# GOAL:
#  1) automate the parallel performance analysis of the binaries (C/C++/Fortran)
#  2) invoke analysis using provided range of tasks/processes with optionally
#     specified step (e.g. 1..32:1)
#  3) in case of MPI code, detect MPI vendor (OMP/IMPI) and test advanced MPI
#     collective optimization via envars. use the most optimal execution from the
#     previous step
#  4) test different compiler flags
#  5) plot graphs of scalability (step 2), histograms of collective calls (step 3),
#     and histograms of compiler flags (step 4)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # note, the module environment should always be at the first place
    batch = BatchFileData()
    src = SrcData()
    test = Tests()
    exec = Executer()
    stat = Statistics()
    thread_range = range(1, 3)

    # Read basic configuration
    batch.read_config(thread_range, 'config.json')
    src.read_config('config.json')

    # print('\n--- start test')

    # print('\n--- report statistics')
    # stat.report_statistics(batch)

    # print('\n--- generate batch script')
    # batch.generate_batch_file(src)
    tmp_dir_name = 'tmp'
    exec.create_wrk_dir()
    exec.create_wrk_copy(src, tmp_dir_name)
    # batch.generate_batch_file(src, tmp_dir_name)
    # batch.generate_interactive_cmd(src, tmp_dir_name)
    # exec.parse_output_for_perf(filename, regex)

    # test.omp_scalability(batch, src, thread_range)
