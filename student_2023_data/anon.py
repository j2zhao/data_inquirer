
import json
import re

def replace_substring_case_insensitive(original_string, old_substring, new_substring):
    pattern = re.compile(re.escape(old_substring), re.IGNORECASE)
    return pattern.sub(new_substring, original_string)


def replace_logs(log, str1, str2 = 'NAME'):
    for key in log:
        if isinstance(log[key], str):
            log[key] = replace_substring_case_insensitive(log[key], str1, str2)
        elif isinstance(log[key], dict):
            log[key] = replace_logs(log[key], str1, str2)
        elif isinstance(log[key], list):
            new_list = []
            for l in log[key]:
                if isinstance(l , str):
                    l2 = replace_substring_case_insensitive(l, str1, str2)
                    new_list.append(l2)
                elif isinstance(l, dict):
                    new_list.append(replace_logs(l, str1, str2))
                else:
                    new_list.append(l)
            log[key] = new_list
    return log

def replace_logs_all(file_name):
    with open(file_name, 'r') as f:
        logs = json.load(f)
    replacement = []
    # print('insert keyword: ')
    # temp = input()
    # while temp != '':
    #     replacement.append(temp)
    #     print('insert keyword: ')
    #     temp = input()
    for log in logs:
        # replacement = []
        # if 'name' in logs[log]:
        #     name = logs[log]['name']
        #     del logs[log]['name']
        #     replacement.append(name)
        # print(name)
        # print('insert keyword: ')
        # temp = input()
        # while temp != '':
        #     replacement.append(temp)
        #     print('insert keyword: ')
        #     temp = input()
        
        for key in replacement:
            logs[log] = replace_logs(logs[log], key, str2 = 'NAME')
    
    with open(file_name, 'w') as f:
        json.dump(logs, f)

replace_logs_all('./logs.json')