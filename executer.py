import os
import shutil
import sys

import io_manager

class Executer:
    
    _root_wrk_dir = os.getenv('PWD')
    _tmp_dir_name = 'tmp'

    def create_dir(self, dir_name):
        """
        Create directory
        :param dir_name: Name of the directory to be created
        """
        full_path = self._root_wrk_dir + '/' + dir_name
        if not os.path.exists(full_path):
            io_manager.print_dbg_info('Creating working directory: ' + full_path)
            os.makedirs(full_path)
        else:
            io_manager.print_dbg_info('Working directory already exists: ' + full_path)


    def copy_src(self, src_data, dir_name):
        src_full_path = src_data.get_src_path()
        dst_full_path = self._root_wrk_dir + '/' + dir_name
        io_manager.print_dbg_info('Copy source files to working directory: '
                                  + src_full_path + ' --> ' + dst_full_path)
        self._copy_tree(src_full_path, dst_full_path)


    def execute(self):
        pass


    def _copy_tree(self, src, dst, symlinks=False, ignore=None):
        if os.path.exists(src):
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, symlinks, ignore)
                else:
                    shutil.copy2(s, d)
        else:
            io_manager.print_err_info('The source directory does not exist: ' + src)
            sys.exit(1)