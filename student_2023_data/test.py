import json
with open('./logs.json', 'r') as f:
        logs = json.load(f)

for log in logs:
    lines = set()
    for l in logs[log]['logs']:
          # if logs[log]['logs'][l]['eerror'] != None and 'User' in logs[log]['logs'][l]['eerror']:
          #       print(logs[log]['logs'][l]['eerror'])
          #       input()
          for line in logs[log]['logs'][l]['code']:
            if 'DIRECTORY' in logs[log]['logs'][l]['code'][line]['code']:
                lines.add(logs[log]['logs'][l]['code'][line]['code'])
    for line in lines:
      print(line)
    input()