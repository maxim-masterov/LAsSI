import json
import os
import sys
import re
import time
import subprocess

from version import *
import io_manager


class BatchFileData:
    """
    Store information about the batch files
    """
    _modules = []

    _system_name = 'Snellius'
    _max_cores_pre_node = 128

    _script_base_name = None
    _exec_options = None
    _envars = []
    _nodes = 1
    _ntasks = 1
    _cpus = 1
    _partition = 'thin'
    _time = 1
    _launcher = 'srun'
    _job_file_ext = 'sh'
    _log_name = 'output.log'
    _asynchronous = False

    def is_asynchronous(self):
        """
        :return: True if sbatch call should be asynchoronous, False otherwise
        """
        return self._asynchronous

    def get_modules(self):
        """
        :return: List of modules
        """
        return self._modules

    def get_system_name(self):
        """
        :return: Name of the system
        """
        return self._system_name

    def get_max_cores_pre_node(self):
        """
        :return: Max number of cores per node on the system
        """
        return self._max_cores_pre_node

    def get_script_base_name(self):
        """
        :return: Base name of the batch script
        """
        return self._script_base_name

    def get_exec_options(self):
        """
        :return: Executable options
        """
        return self._exec_options

    def get_envars(self):
        """
        :return: List of environment variables
        """
        return self._envars

    def get_nodes(self):
        """
        :return: Number of nodes
        """
        return self._nodes

    def set_nodes(self, nodes):
        """
        Set nodes count ('-N' option)
        :return: None
        """
        self._nodes = nodes

    def get_ntasks(self):
        """
        :return: Number of tasks
        """
        return self._ntasks

    def set_ntasks(self, ntasks):
        """
        Set MPI tasks count ('-n' option)
        :return: None
        """
        self._ntasks = ntasks

    def get_cpus(self):
        """
        :return: Number of CPUs
        """
        return self._cpus
    
    def set_cpus(self, cpus):
        """
        Set CPU count ('-c' option)
        :return: None
        """
        self._cpus = cpus

    def get_partition(self):
        """
        :return: Partition name
        """
        return self._partition

    def get_time(self):
        """
        :return: Time constraint
        """
        return self._time

    def get_launcher(self):
        """
        :return: Launcher name
        """
        return self._launcher

    def set_launcher(self, launcher):
        """
        :return: Launcher name
        """
        self._launcher = launcher

    def get_job_file_ext(self):
        """
        :return: Job file extension
        """
        return self._job_file_ext

    def get_log_name(self):
        """
        :return: Name of the log file
        """
        return self._log_name

    def read_config(self, config_file_name):
        """
        Read JSON config file
        :param config_file_name: Name of the config file
        """
        f = open(config_file_name)
        data = json.load(f)

        self._modules = data['modules']

        self._system_name = data['system_data']['name']
        self._max_cores_pre_node = data['system_data']['max_cores_pre_node']

        self._script_base_name = data['batch_data']['script_base_name']
        self._partition = data['batch_data']['partition']
        self._exec_options = data['batch_data']['executable_options']
        self._launcher = data['batch_data']['launcher']
        self._nodes = data['batch_data']['nodes']
        self._ntasks = data['batch_data']['ntasks']
        self._time = data['batch_data']['time']
        
        for envar in data['batch_data']['envars']:
            self._envars.append((envar['envar'], envar['value']))

        f.close()

    def dump_text_to_file(self, filename, text):
        """
        Dump text to file
        :param filename: File name
        :param text: Text to write
        :return: None
        """
        file = open(filename, 'w')
        file.write(text)
        file.close()

    def check_job_state(job_id):
        cmd = 'sacct -j ' + str(job_id) + ' --format=state'
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        res = out.decode('utf-8')
        return res

    def _assemble_file(self, src, name_postfix='', compiler_flag_id=0):
        """
        Generate batch script from the provided input
        :param src: Object of ScrData
        :param name_postfix: Postfix that represents the test case
        :param compiler_flag_id: ID pointing to an element in the list of compiler flags
        :return: Full text of the job script and a parsable header string
        """
        file_shebang = '#!/bin/bash'
        file_version = '#\n' \
                       '# This batch script was autogenerated by CowBerry v{0}\n' \
                       '#\n'.format(VERSION)
        file_header = '###-==[HEADER]==-###'

        if name_postfix != '':
            file_header += '#SBATCH -o ./' + name_postfix + '/output.%j.out\n'

        file_envars = ''
        if not self.get_envars():
            file_envars = '# no environment variables set\n'
        else:
            for envar, value in self.get_envars():
                file_envars += 'export ' + envar + '=' + str(value) + '\n'

        # Compile the code
        file_comp = ''
        if src.get_recompile_flag():
            file_comp = src.get_compile_cmd(compiler_flag_id) + '\n'
        else:
            file_comp = '# do not rebuild sources \n'

        # TODO;
        # 1) check if self._exec_name can be found in the current folder
        # 2) copy self._exec_name to the TMPDIR
        file_body = 'echo "JOBID: ${SLURM_JOB_ID}"\n'
        file_body += 'cp ' + src.get_exec_name() + ' ${TMPDIR}\n'
        file_body += 'WRKDIR=${PWD}\n'
        results_dir = '${WRKDIR}/results' + name_postfix
        if name_postfix != '':
            file_body += 'mkdir ' + results_dir + '\n'
        file_body += 'cd ${TMPDIR}\n'

        file_module = 'module purge\n'
        for module in self.get_modules():
            file_module += 'module load ' + module + '\n'

        file_cmd = self.get_launcher() + ' ' + src.get_exec_name() + ' ' + self.get_exec_options() + '\n'

        file_footer = ''
        if name_postfix != '':
            file_footer = 'cp -r ${TMPDIR} ' + results_dir + '\n'

        full_text = file_shebang + '\n' \
                    + file_version + '\n' \
                    + file_header + '\n' \
                    + file_module + '\n' \
                    + file_envars + '\n' \
                    + file_comp + '\n' \
                    + file_body + '\n' \
                    + file_cmd + '\n' \
                    + file_footer

        return full_text, file_header

    def _assemble_job_file_name(self, wrk_dir, name_postfix):
        """
        Assemble file name of the job script
        :param wrk_dir: Path to the working directory
        :param name_postfix: Postfix that represents the test case
        :return: Job file name
        """
        return wrk_dir + '/' + self.get_script_base_name() \
               + name_postfix + '.' + self.get_job_file_ext()

    def generate_job_script(self, src, wrk_dir='.', name_postfix='', compiler_flag_id=0):
        """
        Generate batch script from the provided input
        :param src: Object of ScrData
        :param wrk_dir: Path to the working directory
        :param name_postfix: Postfix that represents the test case
        :param compiler_flag_id: ID pointing to an element in the list of compiler flags
        :return: Name of the batch file
        """
        file_header = '#SBATCH -N {0}\n' \
                      '#SBATCH -n {1}\n' \
                      '#SBATCH -c {2}\n' \
                      '#SBATCH -p {3}\n' \
                      '#SBATCH -t {4}\n'.format(self.get_nodes(), self.get_ntasks(),
                                                self.get_cpus(), self.get_partition(),
                                                self.get_time())

        full_text, header_str = self._assemble_file(src, name_postfix, compiler_flag_id)

        full_text = full_text.replace(header_str, file_header)

        # io_manager.print_dbg_info('Generated job script:')
        # io_manager.print_info('----------------------------------------', '')
        # io_manager.print_info(full_text, '')
        # io_manager.print_info('----------------------------------------', '')

        batch_file_name = self._assemble_job_file_name(wrk_dir, name_postfix)
        self.dump_text_to_file(batch_file_name, full_text)

        return batch_file_name

    def generate_interactive_job_cmd(self, src, wrk_dir='.', name_postfix=''):
        """
        Generate interactive SLURM command and assemble the bash file that should
        be called by the generated command
        :param src: Object of SrcData
        :param wrk_dir: Path to the working directory
        :param name_postfix: Postfix that represents the test case
        :return: Complete command and bash file name
        """
        cmd_header = '-N {0} ' \
                     '-n {1} ' \
                     '-c {2} ' \
                     '-p {3} ' \
                     '-t {4} '.format(self.get_nodes(), self.get_ntasks(),
                                      self.get_cpus(), self.get_partition(),
                                      self.get_time())

        if name_postfix != '':
            cmd_header += '-o ./' + name_postfix + '/output.%j.out '

        full_text, header_str = self._assemble_file(src, name_postfix)

        # io_manager.print_dbg_info('Generated bash script:')
        # io_manager.print_info('----------------------------------------', '')
        # io_manager.print_info(full_text, '')
        # io_manager.print_info('----------------------------------------', '')

        bash_file_name = self._assemble_job_file_name(wrk_dir, name_postfix)
        self.dump_text_to_file(bash_file_name, full_text)

        complete_cmd_call = 'srun ' + cmd_header

        io_manager.print_dbg_info('Complete command call: ' + complete_cmd_call)
        io_manager.print_dbg_info('Bash file name: ' + bash_file_name)

        return complete_cmd_call, bash_file_name

    def submit_job_script(self, job_file_name):
        """
        Submit job script to the queue
        :param job_file_name: Name of the script
        :return: Job ID
        """
        if job_file_name == '':
            io_manager.print_err_info('Batch file name is empty')
            sys.exit(1)

        # clean up the tmp file
        if os.path.isfile(self.get_log_name()):
            os.remove(self.get_log_name())

        io_manager.print_dbg_info('Submit batch script: ' + job_file_name)

        # Can use --parsable to get JOB_ID right from the sbatch call:
        job_id = ''
        state = ''
        if self.is_asynchronous():
            sbathc_call = 'sbatch --parsable ' + job_file_name
            proc = subprocess.Popen(sbathc_call, stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            if out is None:
                io_manager.print_err_info('Could not get the job ID. Returned value is \'None\'')
            else:
                job_id = out.decode('utf-8').strip()
        else:
            os.system('sbatch --wait ' + job_file_name + ' &> ' + self.get_log_name())
            job_id = self._extract_job_id(self.get_log_name())

            # Report job ID and exit state
            slurm_file_name = 'slurm-' + job_id + '.out'
            state = self._extract_job_state(slurm_file_name)
            if job_id is None:
                io_manager.print_err_info('Could not parse the job ID. Returned value is \'None\'')
            elif state is None:
                io_manager.print_err_info('Could not parse the job state. Returned value is \'None\'')
            else:
                io_manager.print_dbg_info('Job #' + str(job_id) + ' is finished with state: ' + state)

        return job_id, state

    def submit_interactive_job(self, cmd, bash_file_name):
        """
        Submit job interactively (just call for a 'cmd')
        :param cmd: Complete command
        :param bash_file_name: Name of the bash file that should be submitted
        :return: None
        """
        if cmd == '':
            io_manager.print_err_info('Command for the interactive submission is empty')
            sys.exit(1)
        if bash_file_name == '':
            io_manager.print_err_info('Bash file name is empty')
            sys.exit(1)

        os.system('chmod +x ' + bash_file_name)
        io_manager.print_dbg_info('Interactive command: ' + cmd + ' ' + bash_file_name)
        os.system(cmd + ' ' + bash_file_name)

    def _wait_for_file(self, filename, max_wait_sec=120, check_interval=0.4):
        """
        Wait for file. Return True if file was detected within specified 'max_wait_sec'
        limit
        :param filename: filename on task machine
        :param max_wait_sec: how long to wait in seconds
        :param check_interval: how often to check in seconds
        :return: False if waiting was cut short by max_wait_sec limit, True otherwise
        """
        start_time = time.time()
        while True:
            if time.time() - start_time > max_wait_sec:
                io_manager.print_dbg_info('Timeout exceeded (' + str(max_wait_sec)
                                          + ' sec) for ' + filename)
                return False
            if not os.path.isfile(filename):
                time.sleep(check_interval)
                continue
            else:
                break
        return True

    def _extract_job_id(self, filename):
        """
        Extract job id from a file using predefined regex
        :param filename: Name of the file
        :return: Job ID
        """
        self._wait_for_file(filename)
        with open(filename, 'rb') as file:
            file_content = file.read()

        regex = r'Submitted\sbatch\sjob\s*([^\n]+)'
        srch = re.compile(regex, re.MULTILINE)
        job_id = srch.search(file_content)
        if job_id is None:
            io_manager.print_err_info('Cannot extract job ID. Regex search returned \'None\'')
            return None

        return job_id.group(1)

    def _extract_job_state(self, filename):
        """
        Extract job state from a slurm output file using predefined regex
        :param filename: Name of the file
        :return: Job state
        """
        self._wait_for_file(filename)
        with open(filename, 'rb') as file:
            file_content = file.read()

        regex = r'State:\s*([^\s]+)'
        srch = re.compile(regex, re.MULTILINE)
        state = srch.search(file_content)
        if state is None:
            io_manager.print_err_info('Cannot extract the job state. Regex search returned \'None\'')
            return None

        return state.group(1)
