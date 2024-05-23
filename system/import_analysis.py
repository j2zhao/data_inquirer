import re
from methods.annotation_logs import AnnotatedLogs

def extract_imports(code):
    pattern = r'^import (\w+)|^from ([\w.]+) import'
    
    matches = re.findall(pattern, code, re.MULTILINE)
    imports = {match[0] or match[1] for match in matches if match[0] or match[1]}
    imports = {im.split('.')[0] for im in imports}
    return list(imports)

# get all library imports
def imports(annotated_logs):
    annotated_logs.delete_line_query_annotation('import', annotated_logs.logs)
    for findex, name in annotated_logs.get_students().items():
        query_result = annotated_logs.query(file_query = {'index': (findex, 'exact')},  log_query = {"ferror": (None, 'exact')}, line_query = {"content_clean": ('import', 'not')})
        imports = set()
        for log_index, log in query_result[findex]['logs'].items():
            lines = []
            for line_index, line in log['code'].items():
                lines.append(line["content_clean"])
            lines = '\n'.join(lines)
            imports_ = extract_imports(lines)
            imports.update(imports_)
        annotated_logs.add_annotation(list(imports), findex, data_type = 'imports')        
    
    query_result = annotated_logs.query(log_query = {"ferror": (None, 'exact')}, line_query = {"content_clean": ('import', 'contains')})
    annotated_logs.add_line_query_annotation('import', query_result)
    annotated_logs.update_save()

# get export data methods
# get import data methods
def get_data_interaction(annotated_logs:AnnotatedLogs):
    annotated_logs.delete_line_query_annotation('import_data', annotated_logs.logs)
    query_result = annotated_logs.query(line_query ={"content_clean":('csv','contains')})
    annotated_logs.add_line_query_annotation('import_data', query_result)
    query_result = annotated_logs.query(line_query ={"content_clean":('data/','contains')})
    annotated_logs.add_line_query_annotation('import_data', query_result)
    query_result = annotated_logs.query(line_query ={"content_clean":('/data','contains')})
    annotated_logs.add_line_query_annotation('import_data', query_result)
    query_result = annotated_logs.query(line_query ={"content_clean":('write','contains')})
    annotated_logs.add_line_query_annotation('import_data', query_result)
    query_result = annotated_logs.query(line_query ={"content_clean":('path','contains')})
    annotated_logs.add_line_query_annotation('import_data', query_result)
    annotated_logs.update_save()

if __name__ == '__main__':
    annotated_logs = AnnotatedLogs('../student_2023_data/cleaned_data/logs.json')
    imports(annotated_logs)
    get_data_interaction(annotated_logs)