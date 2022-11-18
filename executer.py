import shutil
import sys
import re
import os

import io_manager


class Executer:
    
    _root_dir_name = os.getenv('PWD')
    _wrk_dir_name = 'wrk'
    _full_wrk_dir_path = os.path.join(_root_dir_name, _wrk_dir_name)

    def get_root_dir_name(self):
        return self._root_dir_name

    def get_wrk_dir_name(self):
        return self._wrk_dir_name

    def get_full_wrk_dir_path(self):
        return self._full_wrk_dir_path

    def create_wrk_dir(self):
        self._create_dir(self.get_full_wrk_dir_path())

    def create_wrk_copy(self, src_data, dir_name):
        """
        Make a working copy of the source code
        """
        if src_data.get_recompile_flag():
            self._copy_src(src_data, dir_name)
        else:
            self._copy_bin(src_data, dir_name)

    def execute(self):
        pass

    def parse_output_for_perf(self, filename, regex):
        """
        Parse file 'filename' and find all values that correspond to the 
        'regex'.
        :param filename: Name of the file to parse
        :param regex: Regular expression to look for in the file
        :return: List of found values
        """
        file = open(filename, 'r')
        str = file.read()
        file.close()

        # parse using regex
        srch = re.compile(regex)
        res = srch.findall(str)

        # extract all numbers
        numbers = []
        for elt in res:
            number = [float(x) for x in re.findall(r'-?\d+\.?\d*', elt)]
            numbers.append(number)
        
        return numbers

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

    def _copy_src(self, src_data, dir_name):
        src_full_path = src_data.get_src_path()
        dst_full_path = os.path.join(self.get_full_wrk_dir_path(), dir_name)
        io_manager.print_dbg_info('Copy source files to the working directory: '
                                  + src_full_path + ' --> ' + dst_full_path)
        self._create_dir(dst_full_path)
        self._copy_tree(src_full_path, dst_full_path)

    def _copy_bin(self, src_data, dir_name):
        src_full_path = os.path.join(src_data.get_src_path())
        dst_full_path = os.path.join(self.get_full_wrk_dir_path(), dir_name)
        io_manager.print_dbg_info('Copy a binary file to the working directory: '
                                  + src_full_path + ' --> ' + dst_full_path)
        self._create_dir(dst_full_path)
        src_full_path = os.path.join(src_full_path, src_data.get_exec_name())
        dst_full_path = os.path.join(dst_full_path, src_data.get_exec_name())
        if src_data.check_if_exec_exists():
            shutil.copy2(src_full_path, dst_full_path)

    def _create_dir(self, dir_name):
        """
        Create directory
        :param dir_name: Name of the directory to be created
        """
        full_path = os.path.join(self.get_root_dir_name(), dir_name)
        if not os.path.exists(full_path):
            io_manager.print_dbg_info('Creating directory: ' + full_path)
            os.mkdir(full_path)
        else:
            io_manager.print_dbg_info('Directory already exists: ' + full_path)
