import json
import os

class SrcData:
    _compile_command = ''
    _compiler_flags = ''
    _src_path = ''
    _recompile = True


    def get_compile_cmd(self):
        return self._compile_command + ' ' + self._compiler_flags


    def compile_src(self):
        cmd = self.get_compile_cmd()
        print('\n--- compile sources with: ' + cmd)
        os.system(cmd)


    def read_config(self, config_file_name):
        """
        Read JSON config file
        :param config_file_name: Name of the config file
        """
        f = open(config_file_name)
        data = json.load(f)
        
        self._path_to_src = data['test_setup']['path_to_src']
        self._compile_command = data['test_setup']['compile_command']
        self._compiler_flags = data['test_setup']['compiler_flags']
        self._recompile = data['test_setup']['recompile']

        f.close()
