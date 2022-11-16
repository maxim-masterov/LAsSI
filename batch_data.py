class BatchData:
    modules = []
    batch_script_name = None
    exec_name = None
    exec_options = None
    envars = None
    nodes = 1
    ntasks = 1
    cpus = 1
    partition = 'thin'
    time = 1
    launcher = 'srun'