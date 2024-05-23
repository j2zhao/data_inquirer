from methods.annotation_logs import AnnotatedLogs
annotated_logs = AnnotatedLogs('../student_2023_data/cleaned_data/logs.json')
all_logs = annotated_logs.logs

for file_index, file in all_logs.items():
    if 'llm_use' in file:
        continue
    llm = input()
    if llm == 'y':
        annotated_logs.add_annotation('YES', file_index = file_index, data_type = 'llm_use')
    elif llm == 'm':
        annotated_logs.add_annotation('MAYBE', file_index = file_index, data_type = 'llm_use')
    elif llm == 'n':
        annotated_logs.add_annotation('NO', file_index = file_index, data_type = 'llm_use')
    else:
        raise ValueError()

    annotated_logs.update_save()