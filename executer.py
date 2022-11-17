import os

from io import *

class Executer:
    
    _root_wrk_dir = os.getenv('PWD')
    _tmp_dir_name = 'tmp'

    def create_dir(self, dir_name):
        full_path = self._root_wrk_dir + dir_name
        if not os.path.exists(full_path):
            print_dbg_info('Creating working directory: ' + full_path)
            os.makedirs(full_path)
        else:
            print_dbg_info('Working directory already exists: ' + full_path)

    def execute(self):
        pass