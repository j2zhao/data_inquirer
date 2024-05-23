"""
Python program to replace the compiler

"""
from git import Repo
import os
import time

import sys

import subprocess

COMPILER_COMMAND = 'python' # replace with whatever usually used in the commandline ex. python3

def check_diff(repo):
    hcommit = repo.head.commit
    
    diffs = hcommit.diff(None)

    # for diff_added in diffs.iter_change_type('M'):
    #     print(diff_added)

    if len(diffs) == 0:
        return False
    else:
        return True


def add_commit(id, check_changed = True, push = True):
    """
    Add current changes and commit
    """
    # need to check if anything in repo has changed
    repo = Repo(os.getcwd())
    
    if check_changed:
        changed = check_diff(repo)
    else:
        changed = True    
    if changed:
        repo.git.add('.')
        repo.git.commit('-m', id)
        if push:
            repo.remotes.origin.push()
        return changed
    
    else:
        return changed

if __name__ == '__main__':
    id = str(time.time())
    committed = add_commit(id + '_start', push = False)
    
    command = [COMPILER_COMMAND] + sys.argv[1:]

    process = subprocess.run(command)
    
    with open('./runs.txt', 'a') as f:
        record = '{} , {}, {} , error_code: {} \n'.format(sys.argv[1], committed, id, process.returncode)
        f.write(record)

    add_commit(id + '_end', check_changed = False, push=True)
    
