from collections import defaultdict
import os
import json

def _get_name(string):
  name = string.split('.')[0]
  if '_' in name:
    name = name.split('_')
    return (name[0], int(name[1]))
  else:
    return (name, 0)
  
def _get_files(dire):
    filess = defaultdict(list)
    for f in os.listdir(dire):
        if f.endswith('.txt'):
            name, index = _get_name(f)
            filess[name].append(index)
    
    filess_ = defaultdict(list)
    for name in filess:
        filess[name].sort()
        for i in filess[name]:
            if i == 0:
                filess_[name].append('{}/{}.txt'.format(dire, name))
            else:
                filess_[name].append('{}/{}_{}.txt'.format(dire, name, i))

    return filess_

def parse_file(file_names):
    runs = []
    c = 0
    e = 0
    for file_name in file_names:
        current_run = None
        with open(file_name, 'r') as f:
            for j, line in enumerate(f):
                if line.startswith('new run'):
                    line = line.strip()
                    if current_run != None:
                        runs.append(current_run)
                    current_run = {'code': ''}  
                    current_run['end_time'] = float(line.split(' ')[-1])      
                elif line.startswith('format error: '):
                    line = line.strip()
                    i = len('format error: ')
                    line = line[i:] 
                    if line != 'None':
                        
                        current_run['ferror'] = line
                    else:
                        current_run['ferror'] = None
                
                elif line.startswith('execution error: '):
                    line = line.strip()
                    i = len('execution error: ')
                    line = line[i:]
                    if line != 'None':
                        if line == '':
                          c +=1
                        current_run['eerror'] = line
                        e += 1
                    else:
                        current_run['eerror'] = None
                else:
                    current_run['code'] += line
        if current_run != None:
            runs.append(current_run)
    return runs

def get_runs(base_dir = '../student_2022_data', dataset_dir = 'student_log_data'):
    dataset_dir = os.path.join(base_dir, dataset_dir)
    filess = _get_files(dataset_dir)
    all_runs = {}
    for name, files in filess.items():
        runs = parse_file(files)
        all_runs[name] = runs
    output_path = os.path.join(base_dir, 'cleaned_data')
    output_path = os.path.join(output_path, 'logs.json')
    with open(output_path, 'w') as f:
       json.dump(all_runs, f)

if __name__ == '__main__':
    get_runs()