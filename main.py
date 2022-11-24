import os

from batch_data import BatchFileData
from src_data import SrcData
from tests import Tests
from executer import Executer

# GOAL:
#  1) automate the parallel performance analysis of the binaries (C/C++/Fortran)
#  2) invoke analysis using provided range of tasks/processes with optionally
#     specified step (e.g. 1..32:1)
#  3) in case of an MPI code, detect MPI vendor (OMP/IMPI) and test advanced MPI
#     collective optimization via envars. Use the most optimal execution from the
#     previous step
#  4) test different compiler flags
#  5) plot graphs of scalability (step 2), bar plots of collective calls (step 3),
#     and bar plots of compiler flags (step 4)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test = Tests()

    test.prepare_env('config.json')
    # test.omp_scalability()
    test.compiler_flags()
