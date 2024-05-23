import json
import os
from github import Github
import base64


TOKEN = ''

def file_extractor(commit_message, file_path, repo_name, token = TOKEN):
    g = Github(token)
    repo = g.get_repo(repo_name)
    commits = repo.get_commits()
    file_at_commit = None
    file_changes = None
    for commit in commits:
        if commit.commit.message == commit_message:
            # Get the file at this commit
            for i, file in enumerate(commit.files):
                if file.filename == file_path:
                    file_at_commit = repo.get_git_blob(commit.files[i].sha)
                    file_changes = file.patch
                    break
    return file_at_commit, file_changes


def get_dict_from_log(log_path, repo_name):
    with open(log_path, 'r') as f:
        logs = f.readlines()
    
    formatted_logs = []
    curr_log = {}
    for i, log in enumerate(logs):
        log = log.replace(' ', '').strip()
        print(log)
        name, commit, commit_message, error_code = log.split(',')
        curr_log['file_name'] = name
        curr_log['changed'] = commit
        error_code = ''.join([char for char in error_code if char.isdigit()])

        curr_log['has_error'] = error_code # 0 is no error
        file_path = os.path.join('explore', name)
        code, patch = file_extractor(commit_message + '_start', file_path, repo_name)
        if code != None:
            code = base64.b64decode(code.content)
            code =  code.decode('utf-8')
        curr_log['code'] = code
        curr_log['patch'] = patch
        curr_log['start_time'] = commit_message
        formatted_logs.append(curr_log)
    return formatted_logs


def get_logs_from_repositories(folder):
    all_logs = {}
    base_path = os.path.join(folder, 'valid_repositories')
    for path in os.listdir(base_path):
        student_id  = path
        print(student_id)
        full_path = os.path.join(base_path, path)
        explore_path = os.path.join(full_path, 'explore')
        if os.path.isdir(full_path) and os.path.isdir(explore_path):
            log_path = os.path.join(explore_path, 'runs.txt')
            repo_name = 'CMSC-21800-Fall-2021/final-project-data-exploration-' + student_id
            logs = get_dict_from_log(log_path, repo_name)
            all_logs[student_id] = logs
    
    output_path = os.path.join(folder, 'cleaned_data')
    output_path = os.path.join(output_path, 'logs.json')
    with open(output_path, 'w') as f:
       json.dump(all_logs, f)

def get_missing_logs(folder):
    output_path = os.path.join(folder, 'cleaned_data')
    output_path = os.path.join(output_path, 'logs.json')
    with open(output_path, 'r') as f:
       all_logs = json.load(f)

    base_path = os.path.join(folder, 'valid_repositories')
    for student_id in all_logs:
        for i, log in enumerate(all_logs[student_id]):
            if log['changed'] == 'True' and log['code'] == None:
                full_path = os.path.join(base_path, student_id)
                explore_path = os.path.join(full_path, 'explore')
                repo_name = 'CMSC-21800-Fall-2021/final-project-data-exploration-' + student_id
                file_path = os.path.join('explore', log['file_name'])
                commit_message = str(log['start_time'])+ '_start'
                code, patch = file_extractor(commit_message, file_path, repo_name)
                if code != None:
                    code = base64.b64decode(code.content)
                    code =  code.decode('utf-8')
                print(code)
                print(patch)
                log['code'] == code
                log['patch'] == patch
                print(all_logs[student_id][i])
    
    output_path = os.path.join(folder, 'cleaned_data')
    output_path = os.path.join(output_path, 'logs_2.json')
    with open(output_path, 'w') as f:
       json.dump(all_logs, f)

if __name__ == '__main__':
    #get_logs_from_repositories('../student_chicago_dataset')
    get_missing_logs('../student_chicago_dataset')