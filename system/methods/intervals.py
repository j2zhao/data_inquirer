import copy 
import ast

class CodeInterval(object):
    def __init__(self, lineno, col_offset, end_lineno, end_col_offset):
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset
    
    def __lt__(self, other):
        if self.lineno < other.lineno:
            return True
        elif self.lineno == other.lineno:
            if self.col_offset < other.col_offset:
                return True
            elif self.col_offset == other.col_offset:
                if self.end_lineno < other.end_lineno:
                    return True
                elif self.end_lineno == other.end_lineno:
                    if self.end_col_offset <= other.end_col_offset:
                        return True
                    else:
                        return
                else:
                    return False
                
            else:
                return False
        else:
            return False
    
    def as_tup(self):
        return (self.lineno, self.col_offset, self.end_lineno, self.end_col_offset)

    def intersection(self, other):
        max_lineno = None
        max_col_offset = None
        min_end_lineno = None
        min_end_col_offset = None
        
        if other.lineno < self.lineno:
            max_lineno = self.lineno
            max_col_offset = self.col_offset
        elif other.lineno == self.lineno:
            max_lineno = self.lineno
            max_col_offset = max(other.col_offset, self.col_offset)
        else:
            max_lineno = other.lineno
            max_col_offset = other.col_offset

        if other.end_lineno > self.end_lineno:
            min_end_lineno = self.end_lineno
            min_end_col_offset = self.end_col_offset
        elif self.end_lineno == other.end_lineno:
            min_end_lineno = self.end_lineno
            if other.end_col_offset != -1 and self.end_col_offset != -1:
                min_end_col_offset = min(other.end_col_offset, self.end_col_offset)
            elif other.end_col_offset != -1:
                min_end_col_offset = other.end_col_offset
            else:
                min_end_col_offset = self.end_col_offset
        else:
            min_end_lineno = other.end_lineno
            min_end_col_offset = other.end_col_offset
        
        #ci = CodeInterval(max_lineno, max_col_offset, min_end_lineno, min_end_col_offset)
        isInterval = False
        if min_end_lineno > max_lineno:
            isInterval = True
        elif min_end_lineno == max_lineno:
            if min_end_col_offset >= max_col_offset or min_end_col_offset == -1:
                isInterval = True

        if isInterval:
            return CodeInterval(max_lineno, max_col_offset, min_end_lineno, min_end_col_offset)
        else:
            return None
    
    @staticmethod
    def merge_intervals(intervals_list):
        if len(intervals_list) == 0:
            return []
        intervals_list.sort()
        new_list = []
        temp = None
        for interval in intervals_list:
            if temp == None:
                temp = copy.deepcopy(interval)
            elif temp.end_lineno > interval.lineno or (temp.end_lineno == interval.lineno and (temp.end_col_offset >= interval.col_offset or temp.end_col_offset == -1)):
                if temp.end_lineno > interval.end_lineno:
                    continue
                elif (temp.end_lineno == interval.end_lineno and ((temp.end_col_offset >= interval.end_col_offset and interval.end_col_offset != -1) or temp.end_col_offset == -1)):
                    continue
                else:
                    temp.end_lineno = interval.end_lineno
                    temp.end_col_offset = interval.end_col_offset
            else:
                new_list.append(temp)
                temp = copy.deepcopy(interval)
        if temp != None:
            new_list.append(temp)
        return new_list
    
    @staticmethod
    def _has_segment(n):
        if hasattr(n, 'lineno') and hasattr(n, 'col_offset') and hasattr(n, 'end_lineno') and hasattr(n, 'end_col_offset'):
            if n.lineno != None and n.col_offset != None and  n.end_lineno != None and  n.end_col_offset != None:
                return True
        else:
            return False
    
    @staticmethod
    def as_interval(n):
        if CodeInterval._has_segment(n):
            return CodeInterval(n.lineno, n.col_offset, n.end_lineno, n.end_col_offset)
        else:
            return None
        
    def __str__(self):
        return "(({}, {}), ({}, {}))".format(self.lineno, self.col_offset, self.end_lineno, self.end_col_offset)