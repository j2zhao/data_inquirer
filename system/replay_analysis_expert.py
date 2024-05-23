

# run a segment of code

# run through the dataset again, adding notes

# 
from methods.play_back import CodeRunner
from methods.annotation_logs import AnnotatedLogs
import shutil
from replay.replay_save import replay_from_save_point
from methods.replay_analysis import *

def closest_save(file_index, log_index):
    folder =  f'./temp/{file_index}'
    if not os.path.isdir(folder):
        return 0
    indices = []
    for p in os.listdir(folder):
        dire = os.path.join(folder, p)
        if os.path.isdir(dire):
            indices.append(int(p))
    
    max_index = 0
    for index in indices:
        if index <= int(log_index) and index > max_index:
            max_index = index
    return max_index

def delete_indices(file_index, log_indices):
    for index in log_indices:
        try:
            shutil.rmtree(f'./temp/{file_index}{index}/')
        except:
            pass

def execute_run(annotated_logs, start_index = 0, end_index = -1, file_indices = None, saved_index = [], save_folder = './temp/'):
    if file_indices == None:
        file_indices = list(annotated_logs.get_students().keys())
    for file_index in file_indices:
        runner = CodeRunner()
        indices = annotated_logs.get_sorted_indices(file = file_index)
        start_index = closest_save(file_index, start_index)        
        if isinstance(saved_index, int):
           saved_index_ = indices[::saved_index]
        else:
           saved_index_ = saved_index
        print(saved_index_)
        for log_index in indices:
            if int(log_index) < start_index:
                continue
            elif end_index != -1 and int(log_index) > end_index:
                break
            print(log_index)
            if int(log_index) == start_index and start_index != 0:
                runner = replay_from_save_point(runner, annotated_logs, file_index, log_index, base_folder = save_folder)
                continue
            query_result = annotated_logs.query(file_query = {'index': (file_index, 'exact')}, log_query = {'index': (log_index, 'exact'), "ferror": (None, 'exact'), "eerror": (None, 'exact')}, line_query = {"playback": ('', 'not')})
            if query_result == {}:
                continue
            (out, printed, tm), _ = runner.run_code(query_result[file_index]['logs'], file_index= 
                                                    file_index, folder = save_folder, saved_lines= True, content='playback')

            save_folder_ = os.path.join(save_folder, str(file_index))
            save_folder_ = os.path.join(save_folder_, str(log_index))
            saved_folders = get_lines(save_folder_)
            save_properties_from_logs(annotated_logs, saved_folders, file_index)
            annotated_logs.update_save('replay_expert_logs.json')

            #print(saved_folders)
            #saved_folders = saved_folders[:-1]
            #print(saved_folders[log_index][:-1])
            if str(log_index) not in saved_index_:
                shutil.rmtree(save_folder_)
            else:
                for folder in saved_folders[log_index][:-1]:
                    print(folder[0])
                    shutil.rmtree(folder[0])

        
if __name__ == '__main__':
    annotated_logs = AnnotatedLogs('./replay_expert_logs.json')
    #annotated_logs = AnnotatedLogs('test_logs.json')
    execute_run(annotated_logs, start_index = 0, end_index = -1, saved_index = 20, file_indices = ["1"]) # file_index = ["1"]
    # file_index = "0"
    # log_index = "46"
    # save_folder = './temp/'
    # save_folder_ = os.path.join(save_folder, str(file_index))
    # save_folder_ = os.path.join(save_folder_, str(log_index))
    # saved_folders = get_lines(save_folder_)
    # saved_folders["46"] = saved_folders["46"][9:]
    # print(saved_folders)
    # save_properties_from_logs(annotated_logs, saved_folders, file_index)