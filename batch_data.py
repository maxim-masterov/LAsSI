import json
import os
import sys
import re

from version import *
import io_manager


class BatchFileData:
    _modules = []
    _script_base_name = None
    # _exec_name = None
    _exec_options = None
    _envars = None
    _nodes = 1
    _ntasks = 1
    _cpus = 1
    _partition = 'thin'
    _time = 1
    _launcher = 'srun'
    _bash_file_ext = 'sh'
    _log_name = 'output.log'

    def read_config(self, thread_range, config_file_name):
        """
        Read JSON config file
        :param thread_range: Range of threads count
        :param config_file_name: Name of the config file
        """
        f = open(config_file_name)
        data = json.load(f)
        
        self._modules = data['modules']
        self._script_base_name = data['batch_data']['script_base_name']
        # self._exec_name = data['batch_data']['executable_name']
        self._exec_options = data['batch_data']['executable_options']
        self._launcher = data['batch_data']['launcher']
        self._nodes = data['batch_data']['nodes']
        self._ntasks = data['batch_data']['ntasks']
        self._time = data['batch_data']['time']

        thread_range = range(
            data['test_setup']['thread_range'][0],
            data['test_setup']['thread_range'][1]
        )
        f.close()

    def dump_text_to_file(selft, filename, text):
        """
        Dump text to file
        :param filename: File name
        :param text: Text to write
        :return: None
        """
        file = open(filename, 'w')
        file.write(text)
        file.close()

    def _assemble_file(self, src, name_postfix='', flag_id=0):
        """
        Generate batch script from the provided input
        :param src: Object of ScrData
        :param name_postfix: Postfix that represents the test case
        :return: Full text of the job script and a header string that
                 can be used to parse and modify the header of the file
        """
        file_shebang = '#!/bin/bash'
        file_version = '#\n' \
                    '# This batch script was autogenerated by CowBerry v{0}\n' \
                    '#\n'.format(VERSION)
        file_header = '###-==[HEADER]==-###'

        # if folder doesn't exist it won't be created :(
        if name_postfix != '':
            file_header += '#SBATCH -o ./' + name_postfix + '/output.%j.out\n'

        file_envars = ''
        if not self._envars:
            file_envars = '# no environment variables set\n'
        else:
            for envar, value in self._envars:
                file_envars += 'export ' + envar + '=' + str(value) + '\n'

        # Compile the code
        file_comp = ''
        if src.get_recompile_flag():
            file_comp = src.get_compile_cmd(flag_id) + '\n'
        else:
            file_comp = '# do not rebuild sources \n'

        # TODO;
        # 1) check if self._exec_name can be found in the current folder
        # 2) copy self._exec_name to the TMPDIR
        file_body  = 'echo "JOBID: ${SLURM_JOB_ID}"\n'
        file_body += 'cp ' + src.get_exec_name() + ' ${TMPDIR}\n'
        file_body += 'WRKDIR=${PWD}\n'
        results_dir = '${WRKDIR}/results' + name_postfix
        if name_postfix != '':
            file_body += 'mkdir ' + results_dir + '\n'
        file_body += 'cd ${TMPDIR}\n'

        file_module = 'module purge\n'
        for module in self._modules:
            file_module += 'module load ' + module + '\n'

        file_cmd = self._launcher + ' ' + src.get_exec_name() + ' ' + self._exec_options + '\n'

        file_footer = ''
        if name_postfix != '':
            file_footer  = 'cp -r ${TMPDIR} ' + results_dir + '\n'
            # file_footer += 'cp slurm-${SLURM_JOB_ID}.out ' + name_postfix

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

    def _assemble_bash_file_name(self, wrk_dir, name_postfix):
        return wrk_dir + '/' + self._script_base_name + name_postfix + '.' + self._bash_file_ext

    def generate_batch_file(self, src, wrk_dir='.', name_postfix='', flag_id=0):
        """
        Generate batch script from the provided input
        :param src: Object of ScrData
        :param name_postfix: Postfix that represents the test case
        :return: Name of the batch file
        """
        file_header = '#SBATCH -N {0}\n' \
                      '#SBATCH -n {1}\n' \
                      '#SBATCH -c {2}\n' \
                      '#SBATCH -p {3}\n' \
                      '#SBATCH -t {4}\n'.format(self._nodes, self._ntasks, 
                                                self._cpus, self._partition,
                                                self._time)

        full_text, header_str = self._assemble_file(src, name_postfix, flag_id)

        full_text = full_text.replace(header_str, file_header)

        # io_manager.print_dbg_info('Generated batch script:')
        # io_manager.print_info('----------------------------------------', '')
        # io_manager.print_info(full_text, '')
        # io_manager.print_info('----------------------------------------', '')

        batch_file_name = self._assemble_bash_file_name(wrk_dir, name_postfix)
        self.dump_text_to_file(batch_file_name, full_text)

        return batch_file_name

    def generate_interactive_cmd(self, src, wrk_dir='.', name_postfix=''):
        """
        Generate interactive SLURM command
        :param src: Object of SrcData
        :return: Name of the batch file
        """
        cmd_header = '-N {0} ' \
                     '-n {1} ' \
                     '-c {2} ' \
                     '-p {3} ' \
                     '-t {4} '.format(self._nodes, self._ntasks, 
                                      self._cpus, self._partition,
                                      self._time)

        if name_postfix != '':
            cmd_header += '-o ./' + name_postfix + '/output.%j.out '

        full_text, header_str = self._assemble_file(src, name_postfix)

        # io_manager.print_dbg_info('Generated batch script:')
        # io_manager.print_info('----------------------------------------', '')
        # io_manager.print_info(full_text, '')
        # io_manager.print_info('----------------------------------------', '')

        bash_file_name = self._assemble_bash_file_name(wrk_dir, name_postfix)
        self.dump_text_to_file(bash_file_name, full_text)

        complete_cmd_call = 'srun ' + cmd_header

        io_manager.print_dbg_info('Complete command call: ' + complete_cmd_call)
        io_manager.print_dbg_info('Bash file name: ' + bash_file_name)

        return complete_cmd_call, bash_file_name

    def _extract_job_id(self, filename):
        # file = open(filename, 'r')
        # str = file.read()
        # file.close()
        with open(filename, 'r') as file:
            str = file.read()

        regex = r'Submitted\sbatch\sjob\s*([^\n]+)'
        srch = re.compile(regex, re.MULTILINE)
        job_id = srch.search(str)
        if job_id is None:
            io_manager.print_err_info('Regex search returned None')
            return None

        return job_id.group(1)

    def _extract_job_state(self, filename):
        # file = open(filename, 'r')
        # str = file.read()
        # file.close()

        with open(filename, 'r') as file:
            str = file.read()

        # print(filename, str)
        regex = r'State:\s*([^\s]+)'
        srch = re.compile(regex, re.MULTILINE)
        state = srch.search(str)
        if state is None:
            io_manager.print_err_info('Regex search returned None')
            return None
        
        return state.group(1)

    def submit_batch_script(self, batch_file_name):
        if batch_file_name == '':
            io_manager.print_err_info('Batch file name is empty')
            sys.exit(1)
        
        io_manager.print_dbg_info('Submit batch script: ' + batch_file_name)

        os.system('sbatch --wait ' + batch_file_name + ' &> ' + self._log_name)

        # Report job ID and exit state
        job_id = self._extract_job_id(self._log_name)
        slurm_file_name = 'slurm-' + job_id + '.out'
        # print('slurm_file_name: ' + slurm_file_name)
        state = self._extract_job_state(slurm_file_name)
        io_manager.print_dbg_info('Job #' + job_id +' is finished with state: ' + state)

        return job_id

    def submit_interactively(self, cmd, bash_file_name):
        if cmd == '':
            io_manager.print_err_info('Command for the interactive submission is empty')
            sys.exit(1)
        if bash_file_name == '':
            io_manager.print_err_info('Bash file name is empty')
            sys.exit(1)

        os.system('chmod +x ' + bash_file_name)
        io_manager.print_dbg_info('Interactive command: ' + cmd + ' ' + bash_file_name)
        # os.system(cmd + ' ' + bash_file_name)

# - create tmpdir and report its full path
# - copy sources to tmpdir
# - write job script in tmpdir
# - submit jobscript(s) in tmpdir
#  - export variables
#  - build sources
# - wait untill all jobscripts are finished (async. calls? subprocesses?)
