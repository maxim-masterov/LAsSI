import json
import os

import io_manager


class SrcData:
    """
    Store all information related to the source code, e.g.: the way to compile it, the way to
    extract the valuable data from the output file.
    """
    _compiler_cmd = ''
    _compiler_flags = []
    _src_path = ''
    _recompile = True
    _exec_name = ''
    _perf_regex = ''
    _perf_label = ''
    _list_of_src_files = []
    _threads_list = []
    _tasks_list = []
    _num_repetitions = 1
    _type = 'no_type'

    def get_compiler_cmd(self):
        """
        :return: Compiler command, e.g. 'g++', 'icc'
        """
        return self._compiler_cmd

    def get_compiler_flags(self):
        """
        :return: List of compiler flags
        """
        return self._compiler_flags

    def get_src_path(self):
        """
        :return: Path to source files
        """
        return self._src_path

    def get_recompile_flag(self):
        """
        :return: 'True' if code should be recompiled, 'False' otherwise
        """
        return self._recompile

    def get_perf_regex(self):
        """
        :return: Regular expression to eject the performance values from the
                 output files
        """
        return self._perf_regex

    def get_perf_label(self):
        """
        :return:
        """
        return self._perf_label

    def get_exec_name(self):
        """
        :return: Name of the executable
        """
        return self._exec_name

    def get_list_of_src_files(self):
        """
        :return: List of source files
        """
        return self._list_of_src_files

    def get_threads_list(self):
        """
        :return: Range of threads
        """
        return self._threads_list

    def get_tasks_list(self):
        """
        :return: Range of MPI tasks
        """
        return self._tasks_list

    def get_num_repetitions(self):
        return self._num_repetitions

    def get_type(self):
        return self._type

    def get_compile_cmd(self, compiler_flag_id=0):
        """
        Return a full command to compile the source code
        :param compiler_flag_id: ID of a compiler flag from the config file
        :return: Full compile command
        """
        cmd = self.get_compiler_cmd() + ' ' + self.get_compiler_flags()[compiler_flag_id]
        cmd += ' -o ' + self.get_exec_name()
        for src_file in self.get_list_of_src_files():
            cmd += ' ' + src_file
        return cmd

    def compile_src(self):
        """
        Compile source code
        :return: None
        """
        cmd = self.get_compile_cmd()
        io_manager.print_dbg_info('Compile sources with: ' + cmd)
        os.system(cmd)

    def check_if_exec_exists(self):
        """
        :return: 'True' if executable exists, 'False' otherwise
        """
        return os.path.isfile(self.get_src_path() + '/' + self.get_exec_name())

    def _read_range(self, json_data, range_name):
        range_list = []
        start = json_data['test_setup'][range_name]['start']
        stop = json_data['test_setup'][range_name]['stop']
        step = json_data['test_setup'][range_name]['step']
        multiplier = json_data['test_setup'][range_name]['multiplier']
        if multiplier <= 1:
            range_list = list(range(start,
                                    stop + 1,   # include upper bound in all loops
                                    step))
        else:
            val = json_data['test_setup'][range_name]['start']
            while True:
                range_list.append(val)
                val *= multiplier
                if val > stop:
                    break

        return range_list

    def read_config(self, config_file_name):
        """
        Read JSON config file
        :param config_file_name: Name of the config file
        """
        f = open(config_file_name)
        data = json.load(f)
        
        self._src_path = data['test_setup']['path_to_src']
        self._compiler_cmd = data['test_setup']['compile_command']
        self._compiler_flags = data['test_setup']['compiler_flags']
        self._recompile = data['test_setup']['recompile']
        self._exec_name = data['test_setup']['executable_name']
        self._perf_regex = data['test_setup']['perf_regex']
        self._perf_label = data['test_setup']['perf_label']
        self._list_of_src_files = data['test_setup']['list_of_src_files']
        self._num_repetitions = data['test_setup']['num_repetitions']
        self._type = data['test_setup']['type']

        if self._num_repetitions < 1:
            self._num_repetitions = 1

        self._threads_list = self._read_range(data, 'thread_range')
        self._tasks_list = self._read_range(data, 'tasks_range')

        f.close()
