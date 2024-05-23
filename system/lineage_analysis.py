'''
TODO
'''
import networkx
from methods.ast_history import AnnotatedAST
import matplotlib.pyplot as plt
from methods.annotation_logs import AnnotatedLogs
import pickle
import os


def create_dag(annotated_logs, dire = None, file = None):
    '''
    First create DAG, then try to make heuristics to a tree?
    '''
    graphs = {}
    for findex, name in annotated_logs.get_students().items():
        graphs[findex] = networkx.DiGraph()
        g = graphs[findex]
        runs = annotated_logs.query(file_query = {'index': (findex, 'exact')}, log_query = {"ferror": (None, 'exact'), "eerror": (None, 'exact')}, line_query = {"content_clean": ('', 'not')})
        helper = AnnotatedAST(runs[findex]['logs'],'content_clean')
        indices = annotated_logs.get_sorted_indices(file = findex)
        for log_index in reversed(indices):
            if log_index not in runs[findex]['logs']:
                continue
            print(log_index)
            log = runs[findex]['logs'][log_index]
            line_indices = annotated_logs.get_sorted_indices(file = findex, log = log_index)
            for line_index in reversed(line_indices):
                
                if line_index not in log['code']:
                    continue
                index = (log_index, line_index)
                if not g.has_node(index):
                    g.add_node(index)
                history = helper.fetch_history(log_index, line_index, immediate=True)
                if history == None:
                    continue
                history_lines = [(line) for line, _ in history]
                for h_line in history_lines:
                    if  'import' not in runs[findex]['logs'][h_line[0]]['code'][h_line[1]]['content_clean']:
                        if not g.has_node(h_line):
                            g.add_node(h_line)
                        g.add_edge(index, h_line)
                #input()
    
    if dire != None:
        os.makedirs(dire, exist_ok=True)
        dire = os.path.join(dire, file)
        with open(dire, 'wb') as f:
            pickle.dump(graphs, f)
    return graphs


def test(annotated_logs):
    '''
    First create DAG, then try to make heuristics to a tree?
    '''
    for findex, name in annotated_logs.get_students().items():
        runs = annotated_logs.query(file_query = {'index': (findex, 'exact')}, log_query = {"ferror": (None, 'exact'), "eerror": (None, 'exact')}, line_query = {"content_clean": ('', 'not')})
        helper = AnnotatedAST(runs[findex]['logs'],'content_clean')
        indices = annotated_logs.get_sorted_indices(file = findex)
        for log_index in reversed(indices):
            if log_index not in runs[findex]['logs']:
                continue
            print(log_index)
            log = runs[findex]['logs'][log_index]
            line_indices = annotated_logs.get_sorted_indices(file = findex, log = log_index)
            for line_index in reversed(line_indices):
                # if line_index != str('7'):
                #     continue
                
                if line_index not in log['code']:
                    continue
                print(line_index)
                print(log['code'][line_index]['content_clean'])
                history = helper.fetch_history(log_index, line_index, immediate=True)
                if history == None:
                    continue
                history_lines = [(line) for line, _ in history]
                print('HISTORY')
                for logi, linei in history_lines:
                    print(annotated_logs.logs[findex]['logs'][logi]['code'][linei]['content_clean'])
                input()
    #ß
if __name__ == '__main__':
    annotated_logs = AnnotatedLogs('../student_2022_data/cleaned_data/logs.json')
    #dags = test(annotated_logs)
    create_dag(annotated_logs, dire = '../final_graphs/process/', file = 'student_2022_data.graph')