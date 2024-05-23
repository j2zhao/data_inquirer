
from methods.annotation_logs import AnnotatedLogs

def get_log_num(annotated_logs):
    for file_index, name in annotated_logs.get_students().items():
        num = annotated_logs.get_logs_num(file_index)
        annotated_logs.add_annotation(num, file_index, data_type = 'num_of_logs')
    annotated_logs.update_save()

def get_line_num(annotated_logs, field = 'code', data_type = 'num_of_lines'):
    for findex, name in annotated_logs.get_students().items():
        query_result = annotated_logs.query(file_query = {'index': (findex, 'exact')}, line_query = {field: ('', 'not')})
        for log_index, log in query_result[findex]['logs'].items():
            lines= 0
            for line_index, line  in log["code"].items():
                if line[field] != '':
                    lines +=1
            print(lines)
            annotated_logs.add_annotation(lines, findex, log_index = log_index, data_type = data_type)
    annotated_logs.update_save()


def get_unique_lines(annotated_logs, field = 'code'):
    for file_index, name in annotated_logs.get_students().items():
        repeated_lines = {}
        query_result = annotated_logs.query(file_query = {'index': (file_index, 'exact')}, line_query = {field: ('', 'not')})
        for log_index, log in query_result[file_index]['logs'].items():
            for line_index, line in log['code'].items():
                    line_ = line[field].strip()
                    if line_ != '':
                        if line_ in repeated_lines:
                            repeated_lines[line_] += 1
                            #annotated_logs.add_annotation('duplicate', findex, log_index, line_index)
                        else:
                            repeated_lines[line_] = 1
        annotated_logs.add_annotation(repeated_lines, file_index, data_type = 'repeated_lines')
    annotated_logs.update_save()

line_operations = ['(', '[', '.', '=', ',', ':']
function_operations = ['def ', 'for ', 'if ', 'while ', 'try ', 'with ' ]

def get_line_operations(annotated_logs, field = 'code'):
    all_logs = annotated_logs.logs
    for file_index, logs in all_logs.items():
        for log_index, log in logs['logs'].items():
            for line_index, line in log['code'].items():
                line_ = line[field]
                total_count = 0
                for substring in line_operations:
                    total_count += line_.count(substring)
                annotated_logs.add_annotation(total_count, file_index, log_index, line_index, data_type = 'line_operations_num')
    annotated_logs.update_save()

def get_function_operations(annotated_logs, field = 'code'):
    all_logs = annotated_logs.logs

    for file_index, logs in all_logs.items():
        total_count  = 0
        for log_index, log in logs['logs'].items():
            for line_index, line in log['code'].items():
                line_ = line[field]
                for substring in function_operations:
                    temp = line_.count(substring)
                    # print(line_)
                    # print(line_.count(substring))
                    if temp != 0:
                        # print(line_)
                        # print(temp) 
                        total_count += line_.count(substring)
                        # print(total_count)
                        # raise ValueError()
                    total_count += line_.count(substring)
                    # print(total_count)
        # raise ValueError()
        annotated_logs.add_annotation(total_count, file_index, data_type = 'funct_operations_num')

    annotated_logs.update_save()

if __name__ == '__main__':
    annotated_logs = AnnotatedLogs('../student_2023_data/cleaned_data/logs.json')
    get_log_num(annotated_logs)
    get_line_num(annotated_logs, field = 'code_clean', data_type = 'num_of_lines')
    get_unique_lines(annotated_logs, field = 'code_clean')
    get_line_num(annotated_logs, field = 'comments_clean', data_type = 'num_of_comments')
    get_line_operations(annotated_logs, field = 'content_clean')
    get_function_operations(annotated_logs, field = 'content_clean')