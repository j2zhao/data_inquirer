from methods.annotation_logs import AnnotatedLogs
from methods.ast_history import AnnotatedAST

def get_result_lines(annotated_logs: AnnotatedLogs):
    annotated_logs.delete_line_query_annotation('results', annotated_logs.logs)
    for findex, name in annotated_logs.get_students().items(): 
        runs = annotated_logs.query(file_query = {'index': (findex, 'exact')}, log_query = {"ferror": (None, 'exact')}, line_query = {"content_clean": ('', 'not')})
        helper = AnnotatedAST(runs[str(findex)]['logs'], content='content_clean')
        query_result = annotated_logs.query(file_query = {'index': (findex, 'exact')}, log_query = {"ferror": (None, 'exact')}, line_query ={"content_clean":['OR', ('predict(' ,'contains'), ('score(' ,'contains'), ('predict_proba(' ,'contains')]})
        
        for file in query_result:
            for log_index, log in query_result[file]['logs'].items():
                for line_index, line in log['code'].items():
                    children = helper.fetch_children(log_index, line_index)
                    for indices, _ in children:
                        log, line = indices
                        tags = annotated_logs.logs[file]['logs'][log]['code'][line]['tags']
                        if 'model' not in tags and 'import_data' not in tags:
                            annotated_logs.add_annotation('results', file_index=file, log_index=log, line_index=line)
        annotated_logs.update_save()

def get_model_lines(annotated_logs: AnnotatedLogs):
    annotated_logs.delete_line_query_annotation('model', annotated_logs.logs)
    for findex, name in annotated_logs.get_students().items(): 
        runs = annotated_logs.query(file_query = {'index': (findex, 'exact')}, log_query = {"ferror": (None, 'exact')}, line_query = {"content_clean": ('', 'not')})
        helper = AnnotatedAST(runs[str(findex)]['logs'], content='content_clean')
        query_result = annotated_logs.query(file_query = {'index': (findex, 'exact')}, log_query = {"ferror": (None, 'exact')}, line_query ={"content_clean":['AND', ('sklearn' ,'contains'), ('import' ,'contains'), ('model_selection' ,'not contains'), ('preprocessing' ,'not contains'), \
                                                     ('utils' ,'not contains'), ('decomposition' ,'not contains'), ('metrics' ,'not contains'), ('impute' ,'not contains'), ('ColumnTransformers' ,'not contains') ]})
        for file in query_result:
            for log_index, log in query_result[file]['logs'].items():
                for line_index, line in log['code'].items(): 
                    children = helper.fetch_children(log_index, line_index)
                    for indices, _ in children:
                        log, line = indices
                        annotated_logs.add_annotation('model', findex, log, line)
        
        query_result = annotated_logs.query(file_query = {'index': (findex, 'exact')}, log_query = {"ferror": (None, 'exact')}, line_query ={"content_clean":['AND', ['OR', ('tensorflow' ,'contains'), ('keras' ,'contains')], ('import' ,'contains')]})
        for file_index, file in query_result.items():
            
            for log_index, log in query_result[file_index]['logs'].items():
                for line_index, line in log['code'].items():
                    #print(line["content_clean"])
                    children = helper.fetch_children(log_index, line_index)
                    for indices, _ in children:
                        log, line = indices
                        # print(annotated_logs.logs[findex]['logs'][log]['code'][line]["content_clean"])
                        annotated_logs.add_annotation('model', file_index = findex, log_index = log, line_index = line)
        
        query_result = annotated_logs.query(file_query = {'index': (findex, 'exact')}, log_query = {"ferror": (None, 'exact')}, line_query ={"content_clean":('transform' ,'contains')})
        annotated_logs.delete_line_query_annotation('model', query_result)

        query_result = annotated_logs.query(file_query = {'index': (findex, 'exact')}, log_query = {"ferror": (None, 'exact')}, line_query ={"content_clean":['OR', ('predict(' ,'contains'), ('score(' ,'contains'), ('predict_proba(' ,'contains')]})
        for file in query_result:
            for log_index, log in query_result[file]['logs'].items():
                for line_index, line in log['code'].items():
                    
                    children = helper.fetch_children(log_index, line_index)
                    for indices, _ in children:
                        log, line = indices
                        annotated_logs.delete_annotation(data='model', file_index=file, log_index=log, line_index=line)
        annotated_logs.update_save()
                    
if __name__ == '__main__':
    annotated_logs = AnnotatedLogs('../student_2023_data/cleaned_data/logs.json')
    get_model_lines(annotated_logs)
    get_result_lines(annotated_logs)