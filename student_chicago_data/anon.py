import json


with open('./logs.json', 'r') as f:
    logs = json.load(f)
    
keys = list(logs.keys())
print(keys)
for key in keys:
    for i in range(len(logs[key])):
        print(logs[key][i].keys())
        raise ValueError()
        if logs[key][i]['patch'] != None:
            
        if logs[key][i]['code'] != None:
