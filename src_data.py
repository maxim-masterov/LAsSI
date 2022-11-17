import json
import os

import io_manager

class SrcData:
    _compiler_cmd = ''
    _compiler_flags = ''
    _src_path = ''
    _recompile = True
    _exec_name =''


    def get_compiler_cmd(self):
        return self._compiler_cmd


    def get_compiler_flags(self):
        return self._compiler_flags


    def get_src_path(self):
        return self._src_path


    def get_recompile_flag(self):
        return self._recompile


    def get_compile_cmd(self):
        return self._compiler_cmd + ' ' + self._compiler_flags


    def compile_src(self):
        cmd = self.get_compile_cmd()
        io_manager.print_dbg_info('Compile sources with: ' + cmd)
        os.system(cmd)


    def check_if_exec_exists(self):
        return os.path.isfile(self._exec_name)


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
        self._exec_name = data['batch_data']['executable_name']

        f.close()