import json
import copy
import os

def convert_code_to_lines(code):
    code = code.split('\n')
    lines = []
    for code_line in code:
        line = {}
        line['code'] = code_line
        lines.append(line)
    return lines

def remove_empty_lines(code):
    lines = []
    for code_line in code:
        if code_line['code'] != "":
            lines.append(code_line)
    return lines

def convert_json(file_name):
    with open(file_name, 'r') as f:
        logs = json.load(f)
    for id in logs:
        for log in logs[id]:
            log['code'] = convert_code_to_lines(log['code'])
            log['code'] = remove_empty_lines(log['code']) #convert_code_to_lines(log['code']) #remove_empty_lines(log['code']) 
    
    with open(file_name, 'w') as f:
        json.dump(logs, f)

def tag_lines(file_name):
    with open(file_name, 'r') as f:
        logs = json.load(f)
    
    for id in logs:
        index_log = 0
        for log in logs[id]:
            log['index'] = index_log
            index_log += 1
            index_code = 0
            for line in log['code']:
                line['index'] = index_code
                index_code += 1
    with open(file_name, 'w') as f:
        json.dump(logs, f)

def to_list(file_name):
    with open(file_name, 'r') as f:
        logs = json.load(f)
    
    new_logs = []
    for id in logs:
        new_log = {}
        new_log['name'] = id
        new_log['logs'] = copy.deepcopy(logs[id])
        new_log['tags'] = []
        for l2 in new_log['logs']:
            l2['tags'] = []
            for l3 in l2['code']:
                l3['tags'] = []
        new_logs.append(new_log)
    
    with open(file_name, 'w') as f:
        json.dump(new_logs, f)

def tag_file(file_name):
    with open(file_name, 'r') as f:
        logs = json.load(f)
    
    for i, log in enumerate(logs):
        log['index'] = i
    with open(file_name, 'w') as f:
        json.dump(logs, f)

def convert_to_dict(list_obj):
    dict_obj = {}
    for item in list_obj:
        dict_obj[item['index']] = item
        del dict_obj[item['index']]['index']
    return dict_obj

def convert_index(file_name, file_name_2 = None):
    with open(file_name, 'r') as f:
        all_logs = json.load(f)
    for logs in all_logs:
        for log in logs["logs"]:
            log["code"] = convert_to_dict(log["code"])
        logs["logs"] = convert_to_dict(logs["logs"])
    all_logs = convert_to_dict(all_logs)
    if file_name_2 == None:
        file_name_2 = file_name
    with open(file_name_2, 'w') as f:
        json.dump(all_logs, f)

def individual_files(file_name, dire):
    with open(file_name, 'r') as f:
        all_logs = json.load(f)
    
    for logs in all_logs:
        logs_ = {logs: all_logs[logs]}
        name = all_logs[logs]['name']
        dire_ = os.path.join(dire, name + '.json')
        with open(dire_, 'w') as f:
            json.dump(logs_, f)


if __name__ == '__main__':
    #pass
    convert_json('../student_2023_data/cleaned_data/logs.json')
    #convert_json('../student_2023_data/cleaned_data/logs.json')
    tag_lines('../student_2023_data/cleaned_data/logs.json')
    to_list('../student_2023_data/cleaned_data/logs.json')
    tag_file('../student_2023_data/cleaned_data/logs.json')
    convert_index('../student_2023_data/cleaned_data/logs.json')
    # convert_index('../expert_data/cleaned_data/logs.json')
    #convert_index('../student_2022_data/cleaned_data/logs.json', None)
    #convert_index('../student_2023_data/cleaned_data/logs.json')
    #individual_files('../student_2023_data/cleaned_data/logs.json', '../student_2023_data/cleaned_data/')