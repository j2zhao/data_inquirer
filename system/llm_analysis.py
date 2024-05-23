from methods.ast_history import AnnotatedAST
from methods.annotation_logs import AnnotatedLogs
import re


pattern = r"GENERATED\s*\((.*?)\)"
def get_code(log):
    lines = []
    all_lines = []
    generated = None
    for line_index, line in log['code'].items():
        line_ = line["code"]
        match = re.search(pattern, line_)
        if match or 'GENERATED' in line_:
            if generated != None:
                test = '\n'.join(lines)
                if not 'Hello World' not in test and 'hello world' not in test:
                    all_lines.append((lines, generated))
            if match:
                generated = (line_, match.group(1))
            else:
                generated = (line_, line_)
            lines = []
        else:
            lines.append(line_)
    if generated != None and len(lines) != 0:
        test = '\n'.join(lines)
        if 'Hello' not in test and 'hello world' not in test:
            all_lines.append((lines, generated))
    return all_lines

pattern = r"GENERATED\s*\((.*?)\)"
def get_generated(line):
    line_ = line["code"]
    match = re.search(pattern, line_)
    generated = None
    if match or 'GENERATED' in line_:
        if match:
            generated = (line_, match.group(1))
        else:
            generated = (line_, line_)
    return   generated



def get_comments():
    annotated_logs = AnnotatedLogs('../student_2023_data/cleaned_data/logs.json')          
    query_result = annotated_logs.query(line_query ={"code": ['AND', ('GENERATED' ,'contains')]})
    indices = []
    for file_index, file in query_result.items():
        for log_index, log in file['logs'].items():
            indices.append((file_index, log_index))
            for line_index, line in log['code'].items():
                generated = get_generated(line)
                if generated != None:
                    annotated_logs.add_annotation(generated[1], file_index, log_index, line_index, data_type = 'generated comment')
    lines = []
    meta_data = {}
    logs = annotated_logs.logs
    
    # all_indices = []
    lines_ = {}
    temp_indices = {}
    for i, (file_index, log_index) in enumerate(indices):
        query_result = annotated_logs.query(file_query={"index": (file_index ,'exact')}, log_query={"index": (log_index ,'exact')})
        all_lines = get_code(query_result[file_index]["logs"][log_index])
        if file_index not in temp_indices:
            temp_indices[file_index] = {}
            lines_[file_index] = {}
        for lines, (gen, symbol) in all_lines:
            if symbol in temp_indices[file_index]:
                continue
            temp_indices[file_index][symbol] = []
            lines_[file_index][symbol] = lines
            for line in lines:
                query_result = annotated_logs.query(file_query={"index": (file_index ,'exact')}, line_query={"code": (line ,'exact')})
                for log_index_2 in query_result[file_index]["logs"]:
                    if file_index not in meta_data:
                        meta_data[file_index] = {}
                        meta_data[file_index]['All lines'] = 0
                        meta_data[file_index]['LLM lines'] = 0
                        meta_data[file_index]['LLM Segments'] = {}
                    meta_data[file_index]['LLM lines'] += 1
                    if symbol not in meta_data[file_index]['LLM Segments']:
                        meta_data[file_index]['LLM Segments'][symbol] = 0
                    if (file_index, log_index_2) not in temp_indices[file_index][symbol]:
                        temp_indices[file_index][symbol].append((file_index, log_index_2))
                        meta_data[file_index]['LLM Segments'][symbol] += 1
                    for line_index, line in query_result[file_index]["logs"][log_index_2]['code'].items():
                        annotated_logs.add_annotation(symbol, file_index, log_index_2, line_index, data_type = 'generated line')
    annotated_logs.update_save()
    for file_index in logs.keys():
        for log_index, log in logs[file_index]['logs'].items():
            if file_index not in meta_data:
                meta_data[file_index] = {}
                meta_data[file_index]['All lines'] = 0
                meta_data[file_index]['LLM lines'] = 0
                meta_data[file_index]['LLM Segments'] = {}
            for i in log["code"]:
                if not log["code"][i]['code'].startswith('%') and 'GENERATED' not in log["code"][i]['code'] and 'hello' not in log["code"][i]['code'] and 'Hello' not in log["code"][i]['code']:
                    meta_data[file_index]['All lines'] += 1
    
    percentage = []
    unique_segments = []
    llm_repeats = []
    for file_index in meta_data:
        
        if len(meta_data[file_index]['LLM Segments']) != 0:
            percentage.append(meta_data[file_index]['LLM lines']/meta_data[file_index]['All lines'])
            unique_segments.append(len(meta_data[file_index]['LLM Segments']))
        for symbol, value in meta_data[file_index]['LLM Segments'].items():
            print(value)
            print(lines_[file_index][symbol])
            llm_repeats.append(value)
    return percentage, unique_segments, llm_repeats

if __name__=="__main__":
    percentage, unique_segments, llm_repeats = get_comments()
    print(percentage)
    print(unique_segments)
    print(llm_repeats)