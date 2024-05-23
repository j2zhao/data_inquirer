"""
Playback
"""
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython.utils.capture import CapturedIO
import sys
import io
import time
import inspect
import ast
from methods.ast_history import AnnotatedAST, get_code
from methods.annotation_logs import AnnotatedLogs, get_logs_from_list
import re
from methods.intervals import CodeInterval
from methods.replay_analysis import get_lines, save_properties_from_logs
import os
import shutil

def object_save(folder, local):
    # add imports
    import pickle
    import time
    import os
    import logging
    import types
    if not os.path.exists(folder):
        os.makedirs(folder)
    # setup log errors
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    error_file = os.path.join(folder, 'error.log' )
    file_handler = logging.FileHandler(error_file)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    logging.getLogger('').addHandler(file_handler)

    # get current objects
    names = local.keys()
    user_vars = [item for item in names if not item.startswith("_")]
    for var in user_vars:
        if var in ['object_save', 'get_ipython', 'exit', 'quit', 'open', 'In', 'Out', 'obj_folder', 'function_save']:
            continue
        if isinstance(local[var], types.FunctionType):
            continue
        if isinstance(local[var], types.ModuleType):
            continue
        try:
            file_name = os.path.join(folder, str(var) + '.pickle')
            with open(file_name, 'wb') as f:
                pickle.dump(local[var], f)
        except:
            file_name = os.path.join(folder, str(var) + '.pickle')
            try:
                os.remove(file_name)
            except:
                pass
            logging.error('Could not save this variable: %s', var)
    file_name = os.path.join(folder, 'variables.pickle')
    with open(file_name, 'wb') as f:
        pickle.dump(user_vars, f)

def function_save(folder, function_name, function_line, local):
    import os
    if folder != None:
        folder = os.path.join(folder, function_name)
        folder = os.path.join(folder, function_line)
        object_save(folder, local)

def get_object_save_function():
    source = inspect.getsource(object_save)
    return source

def get_function_save_function():
    source = inspect.getsource(function_save)
    return source

def get_relevant_line(base_folder, file_index, node, code_to_log, before):
    if not hasattr(node, 'start_line') or not hasattr(node, 'end_line'):
        raise ValueError()
    if before:
        block, line = node.start_line
    else:
        block, line = node.end_line
    function_line = str(block) + '_' + str(line) + '_' + str(before)
    folder = os.path.join(base_folder, file_index)
    folder = os.path.join(folder, str(block))
    folder = os.path.join(folder, function_line)
    return folder, function_line


def get_function_call_args(func_def_node, folder = None):
    if folder:
        keyword = ast.keyword(arg='obj_folder', value=ast.Constant(value=folder))
        func_def_node.keywords.append(keyword)
    else:
        keyword = ast.keyword(arg='obj_folder', value=ast.Name(id='obj_folder', ctx=ast.Load()))
        func_def_node.keywords.append(keyword)

def get_function_save_args(function_node):
    function_node.args.args.append(ast.arg(arg='obj_folder', annotation=None))
    function_node.args.defaults.append(ast.arg(arg='None'))
    return function_node

def get_function_save_call(function_name, function_line):
    #function_line = str(block) + '_' + str(line) + '_' + str(before)
    call_str = 'function_save(obj_folder, "{}", "{}", locals())'.format(function_name, function_line)
    call_ast = ast.parse(call_str)
    #call_ast._meta = True
    return call_ast.body[0]

def get_object_save_call(folder):
    call_str = 'object_save("{}", locals())'.format(folder)
    call_ast = ast.parse(call_str)
    #call_ast._meta = True
    return call_ast.body[0]

def update_node(node, custom_functs, file_index, code_to_log, base_folder, funct, function_only = False):  #
    #for node in nodes:
    if isinstance(node, ast.FunctionDef):
        get_function_save_args(node)
        custom_functs.add(node.name)
        node.body, custom_functs = update_node(node.body, custom_functs, file_index, code_to_log, base_folder, funct = node.name, function_only = function_only)
    else:
        match = False
        if hasattr(node, 'body'):
            match = True
            node.body, custom_functs = update_node(node.body, custom_functs, file_index, code_to_log, base_folder, funct, function_only = function_only)
        if hasattr(node, 'orelse'):
            match = True
            node.orelse, custom_functs = update_node(node.orelse, custom_functs, file_index, code_to_log, base_folder, funct, function_only = function_only)
        if hasattr(node, 'finalbody'):
            match = True
            node.finalbody, custom_functs = update_node(node.finalbody, custom_functs, file_index, code_to_log, base_folder, funct, function_only = function_only)
        if isinstance(node, list):
            match = True
            new_nodes = []
            for i, n in enumerate(node):
                if i == 0:
                    if funct:
                        _, function_line = get_relevant_line(base_folder, file_index, n, code_to_log, before = True)
                        n_ =  get_function_save_call(funct, function_line)
                        new_nodes.append(n_)
                    elif not function_only:
                        folder , _ = get_relevant_line(base_folder, file_index, n, code_to_log, before = True)
                        n_  = get_object_save_call(folder)
                        new_nodes.append(n_)
                n, custom_functs = update_node(n, custom_functs, file_index, code_to_log, base_folder, funct, function_only = function_only)
                #new_nodes.append(n)
                if isinstance(n, list):
                    new_nodes.extend(n)
                else:
                    new_nodes.append(n)
                if funct:
                    _, function_line = get_relevant_line(base_folder, file_index, n, code_to_log, before = False)
                    n_ =  get_function_save_call(funct, function_line)
                    new_nodes.append(n_)
                elif not function_only:
                    folder , _ = get_relevant_line(base_folder, file_index, n, code_to_log, before = False)
                    n_  = get_object_save_call(folder)
                    new_nodes.append(n_)
            node = new_nodes
        if isinstance(node, ast.Call):
            match = True
            for n in ast.walk(node.func):
                if isinstance(n, ast.Name):
                    name = n.id
                    break
            if name in custom_functs:
                if funct:
                    get_function_call_args(node)
                else:
                    folder, _ = get_relevant_line(base_folder, file_index, node, code_to_log, before = False) # here
                    get_function_call_args(node, folder)
        if not match:
            for n in ast.iter_child_nodes(node):
                _ , custom_functs = update_node(n, custom_functs, file_index, code_to_log, base_folder, funct, function_only = function_only)
    return node, custom_functs


def run_code(code, ipython):
    #ipython = TerminalInteractiveShell()
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    # Execute the code and capture outputs
    start = time.time()
    output = ipython.run_cell(code)
    end = time.time()
    sys.stdout = old_stdout
    printed = redirected_output.getvalue()
    redirected_output.close()
    # Return the output
    return output, printed, end-start

class CodeRunner:
    def __init__(self):
        # Create a new IPython instance
        self.ipython = TerminalInteractiveShell()
        self.custom_functions = set()

    def run_code(self, code_query, file_index, folder = 'test_save', saved_lines = False, content = 'code'):
        if saved_lines == False:
            code, code_to_log, log_to_code = get_code(code_query, content)
            code = '\n'.join(code)
            return run_code(code, self.ipython), code
        ast_ = AnnotatedAST(code_query, content)
        code = '\n'.join(ast_.code)
        if saved_lines == 'function':
            function_only = True
        else:
            function_only = False
        node, self.custom_functions = update_node(ast_.ast_, self.custom_functions, file_index, ast_.code_to_log, folder, funct = False, function_only=function_only)
        
        code = ast.unparse(node)
        print(code)
        funct = get_object_save_function()
        code = funct + '\n' + code
        funct = get_function_save_function()
        code = funct + '\n' + code
        return run_code(code, self.ipython), code

    def run_code_basic(self, code):
        return run_code(code, self.ipython)
        
def test_coderunner():
    code = get_logs_from_list('test_.json', '/Users/jinjinzhao/Google_Drive/data_science_logging_data/analysis/test_.py')
    logs = AnnotatedLogs('test_.json')
    if os.path.isdir('./test_save'):
        shutil.rmtree('./test_save')
    runner = CodeRunner()
    (out, printed, tm), _ = runner.run_code(logs.logs["0"]["logs"], saved_lines= True, file_index= 
                                                    "0", content='playback')
    
    folders = get_lines('./test_save/0/0')
    save_properties_from_logs(logs, folders, "0")
    logs.update_save()

if __name__ == "__main__":
    test_coderunner()