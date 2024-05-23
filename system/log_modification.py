from methods.annotation_logs import AnnotatedLogs

def remove_comments(annotated_logs):
    all_logs = annotated_logs.logs
    for file_index, file in all_logs.items():
        for log_index, log in file['logs'].items():
            comment_1 = False
            comment_2 = False
            for line_index, line in log['code'].items():
                line_ = line['code']
                line_stripped = line_.strip()
                if not comment_1 and not comment_2:
                    index = line_stripped.find('%')
                    found = False
                    if index == 0:
                        s = ''
                        other  = line_
                        found = True
                    if not found:
                        index_h = line_.find("#")
                        index_c = line_.find("\'\'\'")
                        index_cc = line_.find("\"\"\"")
                        min_value = float('inf')
                        min_type = 0
                        if index_h >= 0 and index_h < min_value:
                            min_type = 1
                            min_value = index_h
                        if index_c >= 0 and index_c < min_value:
                            min_type = 2
                            min_value = index_c
                        if index_cc >= 0 and index_cc < min_value:
                            min_type = 3
                            min_value = index_cc
                        if min_type == 0:
                            s = line_
                            other = ''
                        else:
                            s = line_[:min_value]
                            other = line_[min_value:]
                            other_ = other[3:]
                        if min_type == 2:
                            end = other_.find("\'\'\'")
                            if end == -1:
                                comment_1 = True
                        if min_type == 3:
                            end = other_.find("\"\"\"") 
                            if end == -1:
                                comment_2 = True
                elif comment_1:
                    other = line_
                    end = other.find("\'\'\'")
                    s = ''
                    if end != -1:
                        comment_1 = False

                elif comment_2:
                    other = line_
                    end = other.find("\"\"\"")
                    s = ''
                    if end != -1:
                        comment_2 = False
                annotated_logs.add_annotation(s, file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'content')
                annotated_logs.add_annotation(other, file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'comments')                
    annotated_logs.update_save()

def modify_code(annotated_logs):
    all_logs = annotated_logs.logs
    for file_index, file in all_logs.items():
        for log_index, log in file['logs'].items():
            for line_index, line in log['code'].items():
                line_ = line["content"].strip()
                if line_ == '':
                    annotated_logs.add_annotation('', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'playback')
                elif line_.startswith('%'):
                    annotated_logs.add_annotation('', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'playback')
                elif 'show()' in line_:
                    annotated_logs.add_annotation('', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'playback')
                elif 'read_csv' in line_ and 'training' in line_:
                    l = line["content"].split('pd')[0]
                    code =  l + "pd.read_csv('data/training.csv')"
                    annotated_logs.add_annotation(code, file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'playback')
                elif 'read_csv' in line_ and 'testing' in line_:
                    l = line["content"].split('pd')[0]
                    code =  l + "pd.read_csv('data/testing_X.csv')"
                    annotated_logs.add_annotation(code, file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'playback')
                else:
                    annotated_logs.add_annotation(line["content"], file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'playback')
    annotated_logs.update_save()

def modify_clean_code(annotated_logs):
    all_logs = annotated_logs.logs
    for file_index, file in all_logs.items():
        for log_index, log in file['logs'].items():
            for line_index, line in log['code'].items():
                line_ = line["content"].strip()
                if line_ == '':
                    annotated_logs.add_annotation('', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'content_clean')
                elif line_.startswith('%') or line_.startswith('!'):
                    annotated_logs.add_annotation('', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'content_clean')
                elif 'Hello World' in line_ or 'hello world' in line_:
                    annotated_logs.add_annotation('', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'content_clean')
                elif line_.endswith(','):
                    annotated_logs.add_annotation(line["content"] + '\\', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'content_clean')
                elif 'cd data' in line_:
                    annotated_logs.add_annotation('', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'content_clean')
                
                else:
                    annotated_logs.add_annotation(line["content"], file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'content_clean')
                line_ = line["comments"].strip()
                line_2 = line["code"].strip()
                if line_ == '':
                    annotated_logs.add_annotation('', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'comments_clean')
                elif 'GENERATED' in line_:
                    annotated_logs.add_annotation('', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'comments_clean')
                elif 'Hello' in line_2 or 'hello' in line_2 or 'hi' in line_2:
                    annotated_logs.add_annotation('', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'comments_clean')
                else:
                    annotated_logs.add_annotation(line["comments"], file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'comments_clean')
                
                line_ = line["code"].strip()
                if line_ == '':
                    annotated_logs.add_annotation('', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'code_clean')
                elif line_.startswith('%') or line_.startswith('!'):
                    annotated_logs.add_annotation('', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'code_clean')
                elif 'Hello' in line_ or 'hello' in line_:
                    annotated_logs.add_annotation('', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'code_clean')
                    annotated_logs.add_annotation('', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'code_clean')
                elif line_.endswith(','):
                #    print(line_)
                    annotated_logs.add_annotation(line["code"] + '\\', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'code_clean')
                elif 'GENERATED' in line_:
                    annotated_logs.add_annotation('', file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'code_clean')
                else:
                    annotated_logs.add_annotation(line["code"], file_index = file_index, log_index = log_index, line_index = line_index, data_type = 'code_clean')
                
                
    annotated_logs.update_save()

if __name__ == "__main__":
    annotated_logs = AnnotatedLogs('../student_2022_data/cleaned_data/logs.json')
    remove_comments(annotated_logs)
    modify_code(annotated_logs)
    modify_clean_code(annotated_logs)