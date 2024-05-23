'''
Data Conversion

'''
import numpy as np
import pandas as pd
import os
import pickle
import scipy

def get_lines(folder):
    def line_sort(item):
        _, _, line, before, _ = item
        
        if before:
            return line - 0.5
        else:
            return line
    folders = {} # folder_name, line, before or after
    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        if os.path.isdir(path):
            meta = f.split('_')
            block = meta[0]
            line = int(meta[1])
            if meta[2] == 'True':
                before = True
            else:
                before = False
            if block not in folders:
                folders[block] = []
            folders[block].append((path, block, line, before, None))
            
            for f2 in os.listdir(path):
                path_ = os.path.join(path, f2)
                if os.path.isdir(path_):
                    for f3 in os.listdir(path_):
                        path__ = os.path.join(path_, f3)
                        if os.path.isdir(path__):
                            meta = f3.split('_')
                            block = meta[0]
                            line = int(meta[1])
                            if meta[2] == 'True':
                                before = True
                            else:
                                before = False
                            if f2 not in folders:
                                folders[f2] = []
                            folders[f2].append((path__, block, line, before, f))

    for block in folders:
        folders[block].sort(key=line_sort)
    return folders
    

def get_saved_objs(folder, skip = ['variables']):
    obs = {}
    types = {}
    for file in os.listdir(folder):
        if file.endswith('.pickle'):
            name = file.split('.')[0]
            if name in skip:
                continue
            dire = os.path.join(folder, file)
            with open(dire, 'rb') as f:
                ob = pickle.load(f)
                obs[name] = ob
                types[name] = str(type(ob))
    return obs, types

def fetch_arrays(objs):
    obs = {}
    #obs_pd = {}
    for var, ob in objs.items():
        if isinstance(ob, np.ndarray):
            obs[var] = ob
        elif isinstance(ob, pd.DataFrame):
            obs[var] = ob
        elif isinstance(ob, pd.Series):
            obs[var] = ob
        elif scipy.sparse.issparse(ob):
            obs[var] = ob
    return obs

def equal_arrays(arr1, arr2):
    if type(arr1) != type(arr2):
        return None
    elif type(arr1) == np.ndarray:
        return np.array_equal(arr1, arr2)
    elif type(arr1) == pd.DataFrame or isinstance(arr1, pd.Series):
        return arr1.equals(arr2)
    elif scipy.sparse.issparse(arr1):
        result = arr1 != arr2
        if isinstance(result, bool):
            return result
        else:
            return (arr1 != arr2).nnz == 0

change_dict = {0: 'type changed', 1: 'shape changed', 2: 'indices changed', 3: 'data changed', 4: 'no change'}
def simple_changes(obs_arr1, obs_arr2):
    if len(obs_arr1.keys()) == 0 and len(obs_arr2.keys()) == 0:
        return 'no arrays'
    if len(obs_arr1.keys()) == 0 and len(obs_arr2.keys()) != 0:
        return 'created arrays'
    # no change, changed objects, changed shape
    if obs_arr1.keys() != obs_arr2.keys():
        return 'objects changed'
    else:
        changed = 4
        for key in obs_arr1.keys():
            arr1 = obs_arr1[key]
            arr2 = obs_arr2[key]
            equal = equal_arrays(arr1, arr2)
            if equal == None:
                changed = 0
            elif not equal:
                if arr1.shape != arr2.shape:
                    if changed > 1:
                        changed = 1
                elif isinstance(arr1, pd.DataFrame) and ((not arr1.index.equals(arr2)) or (not (arr1.columns == arr2.columns).all())):
                    if changed > 2:
                        changed = 2
                elif isinstance(arr1, pd.Series)  and not arr1.index.equals(arr2):
                    if changed > 2:
                        changed = 2   
                else:
                    if changed > 3:
                        changed = 3

        return change_dict[changed]

def count_nan(obs_arr1):
    counts = {}
    tcounts = 0
    for key, arr in obs_arr1.items():
        if scipy.sparse.issparse(arr):
            # For sparse matrices: count non-zero elements that are NaN
            count = np.isnan(arr.data).sum()
        elif isinstance(arr, (np.ndarray, pd.Series, pd.DataFrame)):
            # For NumPy arrays or pandas structures: convert to NumPy array and count NaNs
            count = pd.isnull(arr)
            if isinstance(arr, pd.DataFrame) or isinstance(arr, pd.Series):
                count = count.to_numpy()
            count =  count.sum()
        else:
            raise ValueError("Unsupported data type")
        counts[key] = int(count)
        tcounts += int(count)

    return counts, tcounts

def get_pandas_columns(obs_arr1):
    columns = {}
    for key, arr in obs_arr1.items():
        if isinstance(arr, pd.DataFrame):
            cs =  arr.columns.to_list()
            columns[key] = cs
    return columns

def get_shape(obs_arr1):
    shape = {}
    for key, arr in obs_arr1.items():
        shape[key] = arr.shape
    return shape



def save_replay_property(annotated_logs, data, data_type, file_index, log_index, line_index, previous_line = None, origin_funct = None):
    replay_obj = {}
    replay_obj['data'] = data
    if origin_funct != None:
        replay_obj['origin_funct'] = origin_funct
    if previous_line != None:
        replay_obj['previous_line'] = previous_line
    annotated_logs.add_annotation(replay_obj, file_index, log_index = log_index, line_index = line_index, data_type = data_type + "_replay")

def save_properties_from_logs(annotated_logs, saved_folders, file_index):
    for segment in saved_folders:
        prev_arrs = None
        prev_line = None
        for i, info in enumerate(saved_folders[segment]):
            path = info[0]
            block = info[1]
            line = info[2]
            before = info[3]
            origin = info[4]
            if block == segment:
                obs, types = get_saved_objs(path)
                arrs = fetch_arrays(obs)
                counts, counts_ = count_nan(arrs)
                columns = get_pandas_columns(arrs)
                shape = get_shape(arrs)
                if prev_arrs != None:
                    changes = simple_changes(prev_arrs, arrs)
                else:
                    changes = None
                
                if before and i == 0:
                    prev_arrs = arrs
                    prev_line = (block, line, before)
                    continue
                elif before:
                    line_index = str(line - 1)
                else:
                    line_index = str(line)
                
                save_replay_property(annotated_logs, types, 'obj_type', file_index, log_index = block, line_index = line_index, previous_line = prev_line, origin_funct = origin)
                save_replay_property(annotated_logs, changes, 'array_modification', file_index, log_index = block, line_index = line_index, previous_line = prev_line, origin_funct = origin)
                save_replay_property(annotated_logs, counts, 'nan_counts', file_index, log_index = block, line_index = line_index, previous_line = prev_line, origin_funct = origin)
                save_replay_property(annotated_logs, columns, 'columns', file_index, log_index = block, line_index = line_index, previous_line = prev_line, origin_funct = origin)
                save_replay_property(annotated_logs, counts_, 'nan_counts_all', file_index, log_index = block, line_index = line_index, previous_line = prev_line, origin_funct = origin)
                save_replay_property(annotated_logs, shape, 'shape', file_index, log_index = block, line_index = line_index, previous_line = prev_line, origin_funct = origin)


                prev_arrs = arrs
                prev_line = (block, line, before)

if __name__ == '__main__':
    # arr1 = {}
    # arr2 = {}
    # arr1['test'] = np.zeros((10, 10))
    # arr2['test'] = pd.DataFrame(arr1['test'])
    # out = simple_changes(arr1, arr2)
    # print(out)
    # print(scipy.sparse.isspmatrix_equal)
    # raise ValueError()
    path_1 = '../temp/1/177/177_1_False'
    path = '../temp/1/177/177_2_False'
    obs, types = get_saved_objs(path)
    obs_1, types = get_saved_objs(path_1)
    #print(obs)
    #print(types)
    arrs = fetch_arrays(obs)
    arr_1 = fetch_arrays(obs_1)
    # counts, counts_ = count_nan(arrs)
    # columns = get_pandas_columns(arrs)
    # shape = get_shape(arrs)
    print('hello')
    changes = simple_changes(arr_1, arrs)