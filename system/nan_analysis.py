from methods.annotation_logs import AnnotatedLogs
from methods.ast_history import AnnotatedAST

def get_nan(annotated_logs: AnnotatedLogs):
    annotated_logs.delete_line_query_annotation('nan', annotated_logs.logs)
    for findex, name in annotated_logs.get_students().items():
        query_result = annotated_logs.query(file_query = {'index': (findex, 'exact')},  log_query = {"ferror": (None, 'exact')}, line_query = {"content_clean": ['OR', ('na(', 'contains'), ('null', 'contains'), ('NaN', 'contains'), ('interpolate', 'contains'), ('na=', 'contains')]})
        annotated_logs.add_line_query_annotation('nan', query_result)
    annotated_logs.update_save()

if __name__ == '__main__':
    annotated_logs = AnnotatedLogs('../expert_data/cleaned_data/logs.json')
    get_nan(annotated_logs)
