import json
import time
import os
import subprocess
import re

import io_manager
from analysis.omp_analysis import OMPAnalysis
from analysis.compiler_analysis import CompilerAnalysis
from analysis.mpi_analysis import MPIAnalysis
from plot import Plot

def detect_test_case(_config_file_name):
    f = open(_config_file_name)
    data = json.load(f)
    _case_name = data['test_setup']['type']
    f.close()
    return _case_name


# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


def check_job_state(job_id):
    cmd = 'sacct -j ' + str(job_id) + ' --format=state'
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    res = out.decode('utf-8')

    res = """
State 
---------- 
 FAILED
 CANCELLED 
 COMPLETED 
 RUNNING 
 """
    print(res)
    return res


if __name__ == '__main__':

    config_file_name = 'config.json'
    case_name = detect_test_case(config_file_name)
    all_known_cases = ['compiler_flags',
                       'omp_scalability', 'omp_affinity',
                       'mpi_scalability', 'mpi_collective']
    case_found = False

    # # 'sbatch --parsable ' + job_file_name'
    # job_file_name = 'test_omp_scalability_1.sh'
    # full_path_wrk_dir = '/home/maximm/pragma/LAsSI/wrk/run_omp_scalability_1/'
    # full_path_root_dir = '/home/maximm/pragma/LAsSI/'

    # state = check_job_state('1917860')
    
    # if 'COMPLETED' in state:
    #     print('job completed')

    # # os.chdir(full_path_wrk_dir)
    # # # os.system('sbatch --parsable ' + job_file_name)
    # # sbathc_call = 'sbatch --parsable ' + job_file_name
    # # proc = subprocess.Popen(sbathc_call, stdout=subprocess.PIPE, shell=True)
    # # (out, err) = proc.communicate()
    # # job_id = out.decode('utf-8').strip()
    # # print('job_id:', job_id)
    # # os.chdir(full_path_root_dir)
    # exit(0)

    # # A List of Items
    # items = list(range(0, 57))
    # l = len(items)

    # # Initial call to print 0% progress
    # printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    # for i, item in enumerate(items):
    #     # Do stuff...
    #     time.sleep(0.1)
    #     # Update Progress Bar
    #     printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    # exit(0)

    # plt = Plot()

    # x_points = [
    #     [1, 2, 4, 8, 16],
    #     [1, 2, 4, 8, 16],
    #     [1, 2, 4, 8, 16],
    # ]
    # y_points = [
    #     [16, 8, 4, 2, 1],
    #     [16, 9, 5, 3, 2],
    #     [16, 8.5, 4.8, 2.7, 1.9],
    # ]
    # plt.plot_scalability(x_points, y_points, 'scalability')
    # plt.plot_parallel_efficiency(x_points, y_points, 'efficiency')

    for known_case in all_known_cases:
        if case_name == known_case:
            case_found = True
            if 'omp_' in case_name:
                test = OMPAnalysis()
                test.prepare_env(config_file_name)
                test.report_system_info()
                if '_scalability' in case_name:
                    test.run_scalability()
                if '_affinity' in case_name:
                    test.run_affinity()             # WIP
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
