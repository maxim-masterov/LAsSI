
<img src="https://user-images.githubusercontent.com/20205127/205919226-19a957b4-05f7-433d-9861-6aa442a2f76d.png" alt="drawing" style="width:100px;"/>

# LAsSI
LAzy analySIs tool automates the performance evaluation and runtime tuning of an HPC application.

## HowTo
1. Install/load the following Python modules:
- matplotlib
- numpy
- textwrap
- json
- shutil

2. Execute as follows:
```bash
$ python main.py
```

## Configuration file

| Name                 | Description                                                                                   | Example                                                  |
|----------------------|-----------------------------------------------------------------------------------------------|----------------------------------------------------------|
| `modules`            | List of modules that are required by the application                                         | `"modules": ["2022", "foss/2022a"]`                      |
| `batch_data`         | Holds information about the job script defaults                                              |                                                          |
| `script_base_name`   | Base name of the job script. The extension will be added automatically                       | `"script_base_name": "test"`                             |
| `partition`          | Name of the SLURM partition                                                                   | `"partition": "sw"`                                      |
| `nodes`              | Default number of nodes per job                                                               | `"nodes": 1`                                             |
| `ntasks`             | Default number of MPI tasks per job                                                           | `"ntasks": 1`                                            |
| `time`               | Time constraint per job                                                                       | `"time": 5`                                              |
| `envars`             | List of dictionaries with environment variable that should be added to the job script         | `"envars": [{"envar": "OMP_PROC_BIND", "value": "true"}` |
| `launcher`           | Name of the launcher that should be used to run the executable                                | `"launcher": "srun"`                                     |
| `executable_options` | Set of the executable's options                                                               | `"executable_options": "1000000"`                        |
| `test_setup`         | Holds information about the test setup                                                        |                                                          |
| `type` | Type of the test (`omp`, `compiler`, `mpi`)                                                   | `"type": "omp"`|
| `recompile` | `true` if the code should be compiled, `false` if executable already exists and can be reused | `"recompile": true` |
| `path_to_src` | Path to source files and binaries of the testing code                                       | `"path_to_src": "examples"` |
| `compile_command` | Command that should be used to compile the testing code | `"compile_command": "g++"`|
| `compiler_flags` | List of compiler flags that should be used during the compilation of the testing code | `"compiler_flags": ["-O3 -xavx2"]` |
| `executable_name` | Name of the executable (the one to be copied or the one to be compiled) | `"executable_name": "dot.out"` |
| `list_of_src_files` | List of source files that should be used to compile the executable | `"list_of_src_files": ["dot_test.cpp"]` |
| `tasks_range` | Range of MPI tasks to use during the scalability test | `"tasks_range": [1, 1]` |
| `thread_range` | Range of OpenMP threads to use during the scalability test. Note that if `multiplier` is greater than `1`, then the `step` option will be ignored`. | `"thread_range": {"start": 1, "stop": 64, "step": 1, "multiplier": 2}` |
| `num_repetitions` | Number of time each test should be repeated. The results will be reported as averages | `"num_repetitions": 1` |
| `perf_regex` | Regular expression to extract the performance values from the SLURM output file | `"perf_regex": "### Dot-product time:\\s+\\S+\\s+seconds"`
| `perf_label` | Label that should be used to identify the performance in plots | `"perf_label": "time, [s]"` |

---------------------------------------------------------
Image: <a href="https://www.flaticon.com/free-icon/lassi_4681941?term=lassi&page=1&position=1&page=1&position=1&related_id=4681941&origin=search" title="food and restaurant icons">Flaticon</a>
