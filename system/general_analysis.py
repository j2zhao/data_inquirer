
import json
import numpy as np
from collections import Counter
from methods.annotation_logs import AnnotatedLogs



def segments(annotated_logs:AnnotatedLogs):
    logs = annotated_logs.logs
    annotated_logs.delete_line_query_annotation('', annotated_logs.logs, 'category')
    for file_index, file in logs.items():
        for log_index, log in logs[file_index]['logs'].items():
            if log['eerror'] == None and log['ferror'] == None:
                for line_index, line in log['code'].items():
                    segment = None
                    if 'import' in line['tags'] or 'import_data' in line['tags']:
                        segment = 'Auxillary'
                    elif 'model' in line['tags'] or 'results' in line['tags']:
                        segment = 'Modeling'
                    elif 'print' in line['tags'] or 'plt' in line['tags'] or 'expression' in line['tags']:
                        segment = 'Visualization'
                    elif 'nan' in line['tags']:
                        segment = 'Modification'
                    elif line['content_clean'] != '':
                        segment = 'Modification'
                    if segment:
                        annotated_logs.add_annotation(segment, file_index=file_index, log_index=log_index, line_index=line_index, data_type='category')
                    
            else:
                for line_index, line in log['code'].items():
                    if line['content_clean'] != '':
                        annotated_logs.add_annotation('Error', file_index=file_index, log_index=log_index, line_index=line_index, data_type='category')
    annotated_logs.update_save()
                

if __name__ == '__main__':
    annotated_logs = AnnotatedLogs('../expert_data/cleaned_data/logs.json')
    segments(annotated_logs)