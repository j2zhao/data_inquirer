from datetime import datetime
from IPython.core.interactiveshell import InteractiveShell
import time
import os
from IPython.core.magic import Magics, magics_class, line_magic, cell_magic

MAX_SIZE = 10000000

@magics_class
class FetchJSContext(Magics):
        
    @line_magic
    def set_filename(self, filename):
        filename = filename.strip()
        filename = filename.split('/')[-1]
        self.shell.filename = filename.split('.')[0]

def get_log_name(dire, shell):
    # check filename is set
    if not hasattr(shell, 'filename'):
        raise ValueError('did not set filename with magic command') 

    # get index number
    index_dire = os.path.join(dire, '{}_current_index.txt'.format(shell.filename))
    if os.path.isfile(index_dire):
        with open(index_dire, 'r') as f:
            index = int(f.readline())
    else:
        index = 0
        with open(index_dire, 'w') as f:
            f.write(str(index))
    
    # set file_dire
    file_dire = os.path.join(dire, '{}_log_{}.txt'.format(shell.filename, index))
    # if it already exists check file_size
    if os.path.isfile(file_dire):
        fsize = os.path.getsize(file_dire)
    else:
        fsize = 0
    if fsize >= MAX_SIZE:
        index += 1
        index_dire = os.path.join(dire, '{}_current_index.txt'.format(shell.filename))
        with open(index_dire, 'w') as f:
            f.write(str(index))
    # get final file_dire
    file_dire = os.path.join(dire, '{}_log_{}.txt'.format(shell.filename, index))
    return file_dire

def update_record(shell, cell, id, result, start, dire = './code_history'):
    if not os.path.isdir(dire):
        os.mkdir(dire)
    file_dire = get_log_name(dire, shell)
    ferror = '\\'.join(str(result.error_before_exec).split('\n'))
    eerror = '\\'.join(str(result.error_in_exec).split('\n'))
    
    with open(file_dire, 'a') as f:
        f.write('new run: {} \n'.format(id))
        f.write('format error: {} \n'.format(ferror))
        f.write('execution error: {} \n'.format(eerror)) # if execution error is nothing, it is probably a keyboard interupt
        f.write('start: {} \n'.format(start))
        f.write(cell)
        f.write('\n')


def log_run(shell, funct):
    def run_cell(raw_cell, **kwargs):
        start = str(time.time())
        result = funct(raw_cell, **kwargs)
        id = str(time.time())
        update_record(shell, raw_cell, id, result, start)
        return result
    return run_cell

def load_ipython_extension(ipython):
    ipython.register_magics(FetchJSContext)
    ipython.run_cell = log_run(ipython, ipython.run_cell)
