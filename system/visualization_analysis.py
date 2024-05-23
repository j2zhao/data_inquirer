

# get different types of visualization code
from methods.annotation_logs import AnnotatedLogs
from methods.ast_history import AnnotatedAST
import ast

# 
def delete_visualization(annotated_logs):
    annotated_logs.delete_line_query_annotation('plt', annotated_logs.logs)
    annotated_logs.delete_line_query_annotation('print', annotated_logs.logs)
    annotated_logs.delete_line_query_annotation('expression', annotated_logs.logs)
    annotated_logs.update_save()

words = ['remove', 'csv', 'append', 'write', 'investigate', 'pd.set_option']
def keywords(line, list):
    for l in list:
        if l in line:
            return True
    return False

def annotate_visualization(annotated_logs):
    for findex, name in annotated_logs.get_students().items():
        runs = annotated_logs.query(file_query = {'index': (findex, 'exact')}, log_query = {"ferror": (None, 'exact')}, line_query = {"content_clean": ('', 'not')})
        helper = AnnotatedAST(runs[str(findex)]['logs'], content="content_clean")

        query_result = annotated_logs.query(file_query = {'index': (findex, 'exact')}, log_query = {"ferror": (None, 'exact')}, line_query ={"content_clean":['AND', ('plt','contains'), ('import','not contains')]})

        annotated_logs.add_line_query_annotation('plt', query_result)
        query_result = annotated_logs.query(file_query = {'index': (findex, 'exact')}, log_query = {"ferror": (None, 'exact')}, line_query ={"content_clean":('print','contains')})
        annotated_logs.add_line_query_annotation('print', query_result)

        query_result = annotated_logs.query(file_query = {'index': (findex, 'exact')}, log_query = {"ferror": (None, 'exact')}, line_query ={"content_clean":['AND', ('=' ,'not contains'), ('import' ,'not contains'), ('fit', 'not contains'), ('for', 'not contains'), ('if', 'not contains')]})
        for file_index, file in query_result.items():
            for log_index, log in file['logs'].items():
                for line_index, line in log['code'].items():
                    if not line['content_clean'].startswith('%'):
                        nodes = helper.get_top_ast(log_index, line_index)
                        expression = False
                        for _, node in nodes:
                            if isinstance(node, ast.Expr):
                                expression = True
                        if expression and not keywords(line['content_clean'], words):
                            annotated_logs.add_annotation('expression', findex, log_index, line_index)
        annotated_logs.update_save()

if __name__ == '__main__':
    annotated_logs = AnnotatedLogs('../expert_data/cleaned_data/logs.json')
    delete_visualization(annotated_logs)
    #test(annotated_logs)
    annotated_logs = annotate_visualization(annotated_logs)