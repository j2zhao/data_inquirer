'''
Represent logs as items that can be queried upon.

'''

import json
import re
import copy


def get_logs_from_list(file, code, type = 'playback'):
    if isinstance(code, str):
        with open(code, 'r') as f :
            code = f.readlines()
    file_index = 0
    block_index = 0
    log = {}
    log[str(file_index)] = {}
    log[str(file_index)]['logs'] = {}
    log[str(file_index)]['logs'][str(block_index)] = {}
    log[str(file_index)]['logs'][str(block_index)]['code'] = {}
    for index, line in enumerate(code):
        log[str(file_index)]['logs'][str(block_index)]['code'][str(index)] = {}
        log[str(file_index)]['logs'][str(block_index)]['code'][str(index)][type] = line
    
    with open(file, 'w') as f:
        json.dump(log, f)
    return log

class AnnotatedLogs():
    def __init__(self, file_name) -> None:
        if isinstance(file_name, str):
            self.file_name = file_name
            with open(file_name, 'r') as f:
                self.logs = json.load(f)
        else:
            self.logs = file_name

    def add_annotation(self, data, file_index, log_index = None, line_index = None, data_type = None):
        anno_obj = self.logs[str(file_index)]
        if log_index != None:
            anno_obj = anno_obj['logs'][str(log_index)]
            if line_index != None:
                anno_obj = anno_obj['code'][str(line_index)]
        if data_type == None:
            if 'tags' not in anno_obj:
                anno_obj['tags'] = []
            if data not in anno_obj['tags']: 
                anno_obj['tags'].append(data)
        else:
            anno_obj[data_type] = data

    
    def add_line_query_annotation(self, data, query_result, data_type = None):
        for file_index, file in query_result.items():
            for log_index, log in file['logs'].items():
                for line_index, line in log['code'].items():
                    anno_obj = self.logs[file_index]
                    if log_index != None:
                        anno_obj = anno_obj['logs'][log_index]
                        if line_index != None:
                            anno_obj = anno_obj['code'][line_index]
                    if data_type == None:
                        if 'tags' not in anno_obj:
                            anno_obj['tags'] = []
                        if data not in anno_obj['tags']:
                            anno_obj['tags'].append(data)
                    else:
                        anno_obj[data_type] = data

    def delete_line_query_annotation(self, data, query_result, data_type = None):
        
        for file_index, file in query_result.items():
            for log_index, log in file['logs'].items():
                for line_index, line in log['code'].items():
                    anno_obj = self.logs[file_index]
                    if log_index != None:
                        anno_obj = anno_obj['logs'][log_index]
                        if line_index != None:
                            anno_obj = anno_obj['code'][line_index]
                    if data_type == None:
                        while (anno_obj['tags'].count(data)):
                            try:
                                anno_obj['tags'].remove(data)
                            except:
                                pass
                    else:
                        try:
                            del anno_obj[data_type]
                        except:
                            pass

    def delete_annotation(self, file_index, data = None, data_type = None , log_index = None, line_index = None):
        anno_obj = self.logs[str(file_index)]
        if log_index != None:
            anno_obj = anno_obj['logs'][str(log_index)]
            if line_index != None:
                anno_obj = anno_obj['code'][str(line_index)]
        if data_type == None:
            while (anno_obj['tags'].count(data)):
                try:
                    anno_obj['tags'].remove(data)
                except:
                    continue
        else:
            del anno_obj[data_type]

    def match_prop_tags(self, logs, query, index):
        q_, qtype = query
        if qtype == 'exact':
            if logs['tags'] == [q_]:
                return True, set([q_])
        elif qtype == 'regex':
            tags = set()
            match_ = False
            for tag in logs['tags']:
                match = re.findall(q_, tag)
                if len(match) != 0:
                    match_ = True
                    tags.union(set(match))
            return match_, tags      
        elif qtype == 'contains':
            for tag in logs['tags']:
                if q_ == tag:
                    return True, set([q_])
        elif qtype == 'not':
            if not [q_] ==  logs['tags']:
                return True, set(logs['tags'])
        elif qtype == 'not contains':
            for tag in logs['tags']:
                if q_ == tag:
                    return False, set()
            return True, set(logs['tags'])
        else:
            raise ValueError('query type not supported')
        return False, set()

    def match_prop_index(self, logs, query, index):
        q_, qtype = query
        if qtype == 'exact':
            # print('hello')
            # print(index)
            # print(q_)
            if index == q_:
                return True, set([q_])
        elif qtype == 'regex':
            match = re.findall(q_, index)
            if len(match) == 0:
                return False, set()
            else:
                return True, set(match)
        elif qtype == 'contains':
            if q_ in index:
                return True, set([q_])
        elif qtype == 'not':
            if  q_ !=  index:
                return True, set([index])
        elif qtype == 'not contains':
            if not q_ in index:
                return True, set(index)
        else:
            raise ValueError('query type not supported')
        return False, set()


    def match_prop_token(self, logs, query, index):
        q_, qtype = query
        tokens = {logs['tokens'][i][0]: i for i in range(len(logs['tokens']))}
        if qtype == 'exact':
            if list(tokens.keys()) == [q_]:
                return True, set(logs['tokens'])
        elif qtype == 'regex':
            tokens = set()
            match_ = False
            for key_ in tokens:
                match = re.findall(q_, key_)
                if len(match) != 0:
                    match_ = True
                    tokens.add(logs['tokens'][tokens[key_]])
            return match_, tokens      
        elif qtype == 'contains':
            for t in tokens:
                if q_ == t:
                    return True, set([logs['tokens'][tokens[t]]])
        elif qtype == 'not':
            if not [q_] ==  [tokens.keys()]:
                return True, set(logs['tokens'])
        elif qtype == 'not contains':
            for t in tokens.keys():
                if q_ == t:
                    return False, set()
            return True, set(logs['tokens'])
        else:
            raise ValueError('query type not supported')
        return False, set()
    
    def match_prop(self, logs, query, dtype, index):
        if query == None:
            if dtype not in logs:
                return False, set() 
            #     if include_view:
            #         return True  
            if logs[dtype] == None:
                return False, set()     
        q_, qtype = query

        if dtype == 'index':
            return self.match_prop_index(logs, query, index)
        elif dtype == 'tags':
            return self.match_prop_tags(logs, query, index)
        elif dtype == 'tokens':
            return self.match_prop_token(logs, query, index)

        if qtype == 'exact':
            if logs[dtype] == q_:
                return True, set([logs[dtype]])
        elif qtype == 'regex':
            match = re.findall(q_, logs[dtype])
            if len(match) == None:
                return False, set()
            else:
                return True, set(match)
        elif qtype == 'contains':
            if q_ in logs[dtype]:
                return True, set([q_])
        elif qtype == 'not':
            if  q_ !=  logs[dtype]:
                return True, set([logs[dtype]])
        elif qtype == 'not contains':
            if not q_ in  logs[dtype]:
                return True, set(logs[dtype])
        else:
            raise ValueError('query type not supported')
        return False, set()
    
    def match_and(self, logs, query, dtype, index):
        view_ = set()
        for q in query:
            match, view = self.match_logic(logs, q, dtype, index)
            view_.union(view)
            if not match:
                return False, set()
        return True, view_
    
    def match_or(self, logs, query, dtype, index):
        match_ = False
        view_ = set()
        for q in query:
            match, view = self.match_logic(logs, q, dtype, index)
            if match:
                match_ = True
                view_.union(view)
                #return True
        if match_:
            return True, view_
        return False, set()
    
    def match_logic(self, logs, query, dtype, index):
        if query[0] == 'AND':
            return self.match_and(logs, query[1:], dtype, index)
        elif query[0] == 'OR':
            return self.match_or(logs, query[1:], dtype, index)
        else:
            return self.match_prop(logs, query, dtype, index)

    def match_field(self, logs, query, include_view):
        output_logs = {}
        for index, log in logs.items():
            match = True
            view = {}
            for dtype, q_ in query.items():
                match, view_ = self.match_logic(log, q_, dtype, index)
                if not match:
                    break
                view[dtype] = view_
            if match:
                output_logs[index] = log
                if include_view:
                    log['view'] = view
        return output_logs

    
    def query(self, file_query = None, log_query = None, line_query = None, include_view = False):
        '''
        The query is similar the same as mongodb query, but it may be more work to make it compatible
        right now support
        Each query format: {'field': [('string', dtype), ], 'tags': ([['and_field', 'and_field'], ['and_field', 'and_field']], is_exact)}
        '''
        file_logs = copy.deepcopy(self.logs)
        if file_query != None:
            file_logs = self.match_field(file_logs, file_query, include_view)
        logs_logs = {}
        if log_query != None:
            for file_index, file in file_logs.items():
                logs_ = self.match_field(file["logs"], log_query, include_view)
                if len(logs_) != 0:
                    file['logs'] = logs_
                    logs_logs[file_index] = file
        else:
            logs_logs = file_logs
        line_logs = {}
        if line_query != None:
            for file_index, file in logs_logs.items():
                logs = {}
                for log_index, log in file["logs"].items():
                    code_ = self.match_field(log["code"], line_query, include_view)
                    if len(code_) != 0:
                        log['code'] = code_
                        logs[log_index] = log
                
                if len(logs) != 0:
                    file['logs'] = logs
                    line_logs[file_index] = file
        else:
            line_logs = logs_logs
        return line_logs

    def query_lines(self, indices):
        logs = {}
        for file_index, log_index, line_index in indices:
            if file_index not in logs:
                for prop in self.logs[file_index]:
                    if prop != 'logs':
                        logs[file_index] = {}
                        logs[file_index][prop] = copy.deepcopy(self.logs[file_index][prop])
                logs[file_index]['logs'] = {}
            if log_index not in logs[file_index]['logs']:
                for prop in self.logs[file_index]['logs'][log_index]:
                    if prop != 'code':
                        logs[file_index]['logs'][log_index] = {}
                        logs[file_index]['logs'][log_index][prop] = copy.deepcopy(self.logs[file_index]['logs'][log_index][prop])
                logs[file_index]['logs'][log_index]['code'] = {}
            if line_index not in logs[file_index]['logs'][log_index]['code']:
                for prop in self.logs[file_index]['logs'][log_index]['code'][line_index]:
                    logs[file_index]['logs'][log_index]['code'][line_index] = {}
                    logs[file_index]['logs'][log_index]['code'][line_index][prop] = copy.deepcopy(self.logs[file_index]['logs'][log_index]['code'][line_index][prop])
        return logs


    def update_save(self, file_name = None):
        if file_name == None:
            file_name = self.file_name
        with open(file_name, 'w') as f:
            json.dump(self.logs, f)

    def get_students(self):
        names = {}
        for key, log in self.logs.items():
            names[key] = self.logs[key]['name']
        return names
    
    def get_logs_num(self, file_index):
        return len(self.logs[str(file_index)]['logs'])
    
    def get_line_nums(self, file_index, log_index):
        return len(self.logs[str(file_index)]['logs'][str(log_index)]['code'])
    
    def get_sorted_indices(self, file = None, log = None, query_result = None):
        if query_result == None:
            query_result = self.logs
        if file != None:
            query_result = query_result[str(file)]["logs"]
        
        if log != None:
            query_result = query_result[str(log)]["code"]
        
        keys = list(query_result.keys())
        keys = [int(k) for k in keys]
        keys.sort()
        keys = [str(k) for k in keys]
        return keys
    
if __name__ == '__main__':
    annotated_logs = AnnotatedLogs('../../expert_data/cleaned_data/logs.json')
    runs = annotated_logs.query(file_query = {'name': ('v1', 'exact')}, log_query = {"ferror": (None, 'exact')}, line_query = {"code": ('', 'not')})