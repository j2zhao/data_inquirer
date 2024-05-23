from collections import defaultdict
import os
import json


def _get_files(dire):
    files = {}
    for f in os.listdir(dire):
        if f.endswith('.txt'):
            name = f.split('.')[0]
            files[name] = os.path.join(dire, f)
    return files

def parse_file(file_name):
    runs = []
    c = 0
    e = 0
    current_run = None
    with open(file_name, 'r') as f:
        for j, line in enumerate(f):
            if line.startswith('new run'):
                line = line.strip()
                if current_run != None:
                    print(current_run)
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
            elif line.startswith('start:'):
                line = line.strip()
                current_run['start_time'] = float(line.split(' ')[-1]) 
            else:
                current_run['code'] += line
    if current_run != None:
        runs.append(current_run)
    return runs

def get_runs(base_dir = '../expert_data', dataset_dir = 'expert_logs'):
    dataset_dir = os.path.join(base_dir, dataset_dir)
    files = _get_files(dataset_dir)
    all_runs = {}
    for name, file in files.items():
        runs = parse_file(file)
        all_runs[name] = runs
    output_path = os.path.join(base_dir, 'cleaned_data')
    output_path = os.path.join(output_path, 'logs.json')
    print(output_path)
    with open(output_path, 'w') as f:
       json.dump(all_runs, f)

if __name__ == '__main__':
    get_runs(base_dir = '../student_2023_data', dataset_dir = 'student_log_data')