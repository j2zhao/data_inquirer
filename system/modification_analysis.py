import re
from methods.annotation_logs import AnnotatedLogs

def test(annotated_logs:AnnotatedLogs):
    logs = annotated_logs.logs
    for file_index, name in annotated_logs.get_students().items():
        for log_index, log in logs[file_index]['logs'].items():
            if log['eerror'] == None and log['ferror'] == None:
                for line_index, line in log['code'].items():
                    #print(line['tags'])
                    if len(line['tags']) == 0 and line['content_clean'] != '':
                        print(line['content_clean'])
        input()

if __name__ == '__main__':
    annotated_logs = AnnotatedLogs('../student_2023_data/cleaned_data/logs.json')
    test(annotated_logs)
