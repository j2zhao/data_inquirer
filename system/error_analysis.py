from methods.annotation_logs import AnnotatedLogs
import re

def tokenize(code):
    # Tokenize by words, removing non-alphanumeric characters
    tokens = re.findall(r'\b\w+\b', code)
    return set(tokens)

def jaccard_similarity(code1, code2):
    # Get the sets of tokens
    set1 = tokenize(code1)
    set2 = tokenize(code2)
    
    # Calculate intersection and union
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    
    # Compute Jaccard similarity
    if len(union) == 0:
        return 0  # Avoid division by zero
    return len(intersection) / len(union)

def levenshtein_distance(code1, code2):
    import Levenshtein as lev
    # Calculate the Levenshtein distance
    return lev.distance(code1, code2)



def cosine_similarity(code1, code2):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as cs

    vectorizer = TfidfVectorizer()
    
    # Fit and transform the data
    tfidf = vectorizer.fit_transform([code1, code2])
    
    # Compute and return the cosine similarity
    return cs(tfidf[0:1], tfidf[1:2])[0][0]

#

def errors_eval(errors_list, errors, lines, similarity = 0.7):
    max_similarity = None
    max_sim_num = None
    for i, error in enumerate(errors_list):
        if errors[i] != -1:
            continue
        sim = cosine_similarity(error, lines)
        if max_sim_num == None or similarity > max_sim_num:
            max_sim_num = sim
            max_similarity = i
    if max_sim_num != None and max_sim_num >= similarity:
        return max_similarity, max_sim_num
    else:
        return None, max_sim_num


# def update_errors(errors, logs):
#     # if it is another instance of an error
#     # if it is something that is very different

def test(annotated_logs:AnnotatedLogs):
    logs = annotated_logs.logs
    for file_index, file in logs.items():
        print(file_index)
        errors = {} # {error_index: resolution index}
        index = 0
        errors_list = [] # {error_index: lines}
        errors_log = {} # {error_index: log_index}
        errors_log_ = {} # {error_index: log_index_clean}
        errors_after = {} # {error_index: [other_errors, very_different]}

        clean_index = 0
        for log_index, log in logs[file_index]['logs'].items():
            lines = []
            for line_index, line in log['code'].items():
                if line['content_clean'] != '': 
                    lines.append(line['content_clean'])
            
            lines = '\n'.join(lines)
            if len(lines) == 0:
                continue
            closest_error, max_signal = errors_eval(errors_list, errors, lines, similarity = 0.5)
            if log['eerror'] != None or log['ferror'] != None:
                if closest_error == None:
                    for e in errors:
                        if errors[e] == -1:
                            errors_after[e][1] += 1
                    errors_list.append(lines)
                    errors[index] = -1
                    errors_log[index] = int(log_index)
                    errors_log_[index] = clean_index
                    errors_after[index] = [0,0]
                    index +=1
                    
                else:
                    for e in errors:
                        if errors[e] == -1 and e != closest_error:
                            errors_after[e][1] += 1
                        if e == closest_error:
                            errors_after[e][0] += 1
                    errors_list[closest_error] = lines

            else:
                
                if closest_error != None:
                    
                    if errors[closest_error] == -1:
                        errors[closest_error] = clean_index - errors_log_[closest_error]

                for e in errors:
                    if errors[e] == -1 and e != closest_error:
                        errors_after[e][1] += 1
            clean_index += 1
        annotated_logs.add_annotation(errors, file_index=file_index, data_type='error_fix')
        annotated_logs.add_annotation(errors_log, file_index=file_index, data_type='errors')
        annotated_logs.add_annotation(errors_after, file_index=file_index, data_type='errors_after')
    annotated_logs.update_save()

if __name__ == '__main__':
    annotated_logs = AnnotatedLogs('../expert_data/cleaned_data/logs.json')
    #dags = test(annotated_logs)
    test(annotated_logs)