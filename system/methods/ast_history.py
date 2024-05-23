"""
Given a set of annotations -> annotated the ast?
Do I do this for all the dataset? -> let's specify which ones?

"""
import ast
import time
from methods.intervals import CodeInterval
import networkx as nx
import copy

def get_code(logs, content = 'code'):
        code = []
        code_to_log = {}
        log_to_code = {}
        code_index = 0
        for log_index, log in logs.items():
            log_to_code[log_index] = {}
            for line_index, line in log["code"].items():
                code.append(line[content])
                code_to_log[code_index] = (log_index, line_index)
                log_to_code[log_index][line_index] = code_index
                code_index += 1
        return code, code_to_log, log_to_code

def set_line(node, code_to_log):
    for n in ast.walk(node):
        interval = CodeInterval.as_interval(n)
        if interval != None:
            n.start_line = code_to_log[n.lineno - 1]
            n.end_line = code_to_log[n.end_lineno - 1]
    return node

class AnnotatedAST():
    def __init__(self, logs, content = 'playback') -> None:
        self.var_map = {} #variale map
        self.funct_map = {}
        self.funct = set()
        self.logs = logs
        # ingest logs into lines of code
        # create a mapping between original logs and new "file"
        self.code, self.code_to_log, self.log_to_code = get_code(logs, content)
        # ingest as AST object
        code_ = []
        for code in self.code:
            if code.endswith('\n'):
                code_.append(code[:-1])
            else:
                code_.append(code)
        self.code = code_
        self.ast_ = ast.parse('\n'.join(self.code))
        self.ast_ = set_line(self.ast_, self.code_to_log)
        self._annotate_AST(self.ast_, 0)

    def _add_assign(self, target, node):
        if isinstance(target, ast.List) or isinstance(target, ast.Tuple):
            for t2 in target.elts:
                self._add_assign(t2, node)
        else:
            if isinstance(target, ast.Name):
                if target.id not in self.var_map:
                    self.var_map[target.id] = []
                self.var_map[target.id].append(((node), 'name'))
            elif isinstance(target, ast.Subscript):
                if isinstance(target.value, ast.Name):
                    if target.value.id not in self.var_map:
                        self.var_map[target.value.id] = []
                    self.var_map[target.value.id].append(((node, target.slice), 'subscript'))
                elif isinstance(target.value, ast.Attribute):
                    if target.value.value.id not in self.var_map:
                        self.var_map[target.value.value.id] = []
                    self.var_map[target.value.value.id].append(((node, target.slice, target.value.attr), 'subscript/attribute'))
                else:
                    self._add_assign(target.value, node)
                    #print(ast.dump(target))
                    #raise NotImplementedError()
            elif isinstance(target, ast.Starred):
                if isinstance(target.value, ast.Name):
                    if target.value.id not in self.var_map:
                        self.var_map[target.value.id] = []
                    self.var_map[target.value.id].append(((node), 'name'))
                else:
                    raise NotImplemented()
            elif isinstance(target, ast.Attribute):
                if isinstance(target.value, ast.Name):
                    if target.value.id not in self.var_map:
                        self.var_map[target.value.id] = []
                    self.var_map[target.value.id].append(((node, target.attr), 'attribute'))
                else:
                    pass
    
    def _add_ref(self, node):
        '''
        TODO: fix bug in case where the variable is redefined as a function
        '''
    
        if node.id in self.var_map:
            for i in range(len(self.var_map[node.id]) - 1, -1, -1):
                parent_node, type = self.var_map[node.id][i]
                if type == 'name':
                    if not hasattr(node, '_lineage'):
                        node._lineage = []
                    node._lineage.append(parent_node)
                    if not hasattr(parent_node, '_children'):
                        parent_node._children = []
                    parent_node._children.append(node)
                    break
                elif type == 'attribute':
                    parent_node = parent_node[0]
                    if not hasattr(node, '_lineage'):
                        node._lineage = []
                    node._lineage.append(parent_node)
                    if not hasattr(parent_node, '_children'):
                        parent_node._children = []
                    parent_node._children.append(node)
                elif type == 'subscript':
                    parent_node = parent_node[0]
                    if not hasattr(node, '_lineage'):
                        node._lineage = []
                    node._lineage.append(parent_node)
                    if not hasattr(parent_node, '_children'):
                        parent_node._children = []
                    parent_node._children.append(node)
        elif node.id in self.funct_map:
            parent_node = self.funct_map[node.id][-1][0][0]
            if not hasattr(node, '_lineage'):
                node._lineage = []
            node._lineage.append(parent_node)
            if not hasattr(parent_node, '_children'):
                parent_node._children = []
            parent_node._children.append(node)
    
    def _annotate_AST(self, node, context, parent=None):
        node._parent = parent  # Annotate the current node with its parent
        node._id = time.time()
        node._context = context
        for child in ast.iter_child_nodes(node):
            self._annotate_AST(child, context + 1, node)

        if isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Name):
                self._add_ref(node.target)
        
        if isinstance(node, ast.Name):

            if isinstance(node.ctx, ast.Load):
                self._add_ref(node)

        if isinstance(node, ast.Assign):
            for target in node.targets:
                self._add_assign(target, node)
        if isinstance(node, ast.AnnAssign) or isinstance(node, ast.AugAssign):
            self._add_assign(node.target, node)
        if isinstance(node, ast.NamedExpr):
            self._add_assign(node.target, node)
        if isinstance(node, ast.Import):
            for n in node.names:
                if n.asname == None:
                    asname = n.name
                else:
                    asname = n.asname
                if asname not in self.funct_map:
                    self.funct_map[asname] = []
                self.funct_map[asname].append(((node,n.name), 'import'))
        
        if isinstance(node, ast.ImportFrom):
            module = node.module
            for n in node.names:
                if n.asname == None:
                    asname = n.name
                else:
                    asname = n.asname
                if asname not in self.funct_map:
                    self.funct_map[asname] = []
                self.funct_map[asname].append(((node, n.name, module), 'import'))
        
        if isinstance(node, ast.FunctionDef):
            if node.name not in self.funct_map:
                self.funct_map[node.name] = []
            self.funct_map[node.name].append(((node, 0), 'function'))

    def _get_relevant_ast(self, node, code_interval, control = True):
        relevant_nodes = []
        has_segment = CodeInterval._has_segment(node)
        if has_segment:
            if isinstance(node, ast.Try):
                for n in ast.iter_child_nodes(node):
                    relevant_nodes += self._get_relevant_ast(n, code_interval, control)
            if not control:
                if isinstance(node, ast.For) or isinstance(node, ast.While) or isinstance(node, ast.With) or isinstance(node, ast.If) or isinstance(node, ast.FunctionDef):
                    for n in ast.iter_child_nodes(node):
                        relevant_nodes += self._get_relevant_ast(n, code_interval, control)
                else:
                    interval = code_interval.intersection(CodeInterval.as_interval(node))
                    if interval != None:
                        relevant_nodes.append(node)
            else:
                interval = code_interval.intersection(CodeInterval.as_interval(node))
                if interval != None:
                    relevant_nodes.append(node)
        
        if not (has_segment and len(relevant_nodes) == 0):
            for n in ast.iter_child_nodes(node):
                relevant_nodes += self._get_relevant_ast(n, code_interval, control)
        return relevant_nodes
    
    def _fetch_history(self, node, graph, nodes, immediate = True):
        if node in nodes:
            return graph
        nodes.append(node)
        if isinstance(node, ast.If):

            for n in ast.walk(node.test):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                    graph = self._fetch_history(n, graph, nodes)
        elif isinstance(node, ast.For):
            for n in ast.walk(node.iter):
                if isinstance(n, ast.Name)  and isinstance(n.ctx, ast.Load):
                    graph = self._fetch_history(n, graph, nodes)
        elif isinstance(node, ast.While):
            for n in ast.walk(node.test):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                    graph = self._fetch_history(n, graph, nodes)
        elif isinstance(node, ast.With):
            for item in node.items:
                for n in ast.walk(item):
                    if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                        graph = self._fetch_history(n, graph, nodes)
        elif isinstance(node, ast.Name):
            if hasattr(node, '_lineage'):
                for n in node._lineage:
                    graph.add_node(n)
                    graph.add_node(node)
                    graph.add_edge(node, n)
                    if not immediate:
                        graph = self._fetch_history(n, graph, nodes)
        elif isinstance(node, ast.FunctionDef):
            pass
        else:
            for n in ast.walk(node):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                    graph = self._fetch_history(n, graph, [])
        return graph
    
    def _fetch_code(self, code_interval):
        code = self.code
        code = code[(code_interval.lineno):code_interval.end_lineno]
        
        code[0] = code[0][code_interval.col_offset:]
        code[-1] = code[-1][:code_interval.end_col_offset]
        return code
    
    def _remove_successors(self, graph, node):
        direct_path_nodes = [node]
        queue = [node]
        while queue:
            current_node = queue.pop(0)
            successors = list(graph.successors(current_node))
            direct_path_nodes += successors
            queue.extend(successors)

        graph.remove_nodes_from(direct_path_nodes)
        return graph
    
    def fetch_history(self, log_index, line_index, end_log_index = None, end_line_index = None, immediate = False, outside = True):
        '''
        outside: if False, do not include lineage of anything that has annotations or is the parent of other nodes
        '''
        # Get log_index and line_index
        try:
            start_line = self.log_to_code[str(log_index)][str(line_index)]
            if end_line_index != None and end_log_index != None:
                end_line = self.log_to_code[str(end_log_index)][str(end_line_index)]
            else:
                end_line = start_line
        except:
            return None
    
        code_interval = CodeInterval(start_line + 1, 0, end_line + 1, -1)
        # Note we include control statements, and history of statements 
        nodes = self._get_relevant_ast(self.ast_, code_interval)
        graph = nx.DiGraph()
        #print('hello')
        for node in nodes: # we don't want nodes

            graph.add_node(node)
            graph = self._fetch_history(node, graph, [])
        #print('hello2')
        if not outside:
            queue = []
            for n in nodes:
                for m in graph.successors(n):
                    queue.append(m)
            while queue:
                m = queue.pop(0)
                in_graph = True
                if m in graph:
                    if hasattr(m, '_children'):
                        for c in m._children:
                            if not graph.has_node(c):
                                in_graph = False
                    if not in_graph:
                        self._remove_successors(graph, m)
                    else:
                        queue.extend(graph.successors(m))
        if immediate:
            remove_nodes = []
            for m in graph:
                dir_parent = False
                for n in nodes:
                    if hasattr(m, '_children'):
                        if n in m._children:
                            dir_parent = True
                if not dir_parent:
                    remove_nodes.append(m)
            for n in remove_nodes:
                graph.remove_node(n)
        intervals = []
        for node in graph.nodes:
            if CodeInterval._has_segment(node):
                interval = CodeInterval.as_interval(node)
                intervals.append(interval)
        
        intervals = CodeInterval.merge_intervals(intervals)
        code_segments = []
        for interval in intervals:
            for i in range(interval.lineno - 1, interval.end_lineno):
                interval_ = CodeInterval(i, 0, i + 1, -1)
                code = self._fetch_code(interval_)
                line = self.code_to_log[i]
                code_segments.append((line, code))
        return code_segments
    
    def _fetch_children(self, node, children):
        if isinstance(node, ast.If):
            if node not in children:
                children.append(node)
            for n in ast.walk(node.test):
                if isinstance(n, ast.Name):
                    children = self._fetch_children(n, children)
            return children
        elif isinstance(node, ast.For):
            if node not in children:
                children.append(node)
            for n in ast.walk(node.iter):
                if isinstance(n, ast.Name):
                    children = self._fetch_children(n, children)
            return children
        elif isinstance(node, ast.While):
            if node not in children:
                children.append(node)
            for n in ast.walk(node.test):
                if isinstance(n, ast.Name):
                    children = self._fetch_children(n, children)
            return children
        elif isinstance(node, ast.With):
            if node not in children:
                children.append(node)
            for n in ast.walk(node.items):
                if isinstance(n, ast.Name):
                    children = self._fetch_children(n, children)
            return children
        elif isinstance(node, ast.FunctionDef):
            if node not in children:
                children.append(node)
            for n in ast.walk(node.args):
                if isinstance(n, ast.Name):
                    children = self._fetch_children(n, children)
            return children
        else:
            if CodeInterval._has_segment(node):
                if node not in children:
                    children.append(node)
                temp = self._get_relevant_ast(self.ast_, CodeInterval.as_interval(node), control=False)
                for t in temp:
                    if t not in children:
                        children.append(t)
            else:
                # TODO: Fix the children stuff here
                return children
            for t in temp:
                if hasattr(t, '_children'):
                    for n in t._children:
                        if n not in children:
                            children = self._fetch_children(n, children)
            return children

    def fetch_children(self, log_index, line_index, end_log_index = None, end_line_index = None):
        '''
        Note for children, we don't include control or function inner block code right now
        Consider converting to graph -> probably don't need to right now.
        '''
        # Get log_index and line_index
        start_line = self.log_to_code[str(log_index)][str(line_index)]
        if end_line_index != None and end_log_index != None:
            end_line = self.log_to_code[str(end_log_index)][str(end_line_index)]
        else:
            end_line = start_line
        code_interval = CodeInterval(start_line + 1, 0, end_line + 1, -1)
        
        nodes = self._get_relevant_ast(self.ast_, code_interval, control = False)
        #print(nodes)
        #print('Chidren')
        has_children = False
        for node in nodes:
            if hasattr(node, '_children'):
                has_children = True
                #raise ValueError()
        nodes_2 = copy.copy(nodes)
        for node in nodes:
            nodes_2 = self._fetch_children(node, nodes_2)
        #print(nodes_2)
        # don't consider function definitions in the interval
        intervals = []
        for node in nodes_2:
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef) or isinstance(node, ast.ClassDef):
                continue
            if CodeInterval._has_segment(node):
                interval = CodeInterval.as_interval(node)
                intervals.append(interval)
        intervals = CodeInterval.merge_intervals(intervals)
        code_segments = []
        for interval in intervals:
            for i in range(interval.lineno - 1, interval.end_lineno):
                interval_ = CodeInterval(i, 0, i + 1, -1)
                code = self._fetch_code(interval_)
                line = self.code_to_log[i]
                code_segments.append((line, code))
        return code_segments

    
    def get_top_ast(self, log_index, line_index, end_log_index = None, end_line_index = None, control = False, outside = False):
        try:
            start_line = self.log_to_code[str(log_index)][str(line_index)]
        except:
            return []
        if end_line_index != None and end_log_index != None:
            end_line = self.log_to_code[end_log_index][end_line_index]
        else:
            end_line = start_line
        code_interval = CodeInterval(start_line + 1, 0, end_line + 1, -1)
        nodes = self._get_relevant_ast(self.ast_, code_interval, control)
        if not outside:
            nodes_ = []
            for node in nodes:
                if CodeInterval._has_segment(node):
                    interval = CodeInterval.as_interval(node)
                    if interval.intersection(code_interval):
                        nodes_.append(node)
            nodes = nodes_
        
        nodes_ = []
        for node in nodes:
            if CodeInterval._has_segment(node):
                interval = CodeInterval.as_interval(node)
                code_segments = []
                for i in range(interval.lineno - 1, interval.end_lineno):
                    interval_ = CodeInterval(i, 0, i + 1, -1)
                    code = self._fetch_code(interval_)
                    line = self.code_to_log[i]
                    code_segments.append((line, code)) 
                nodes_.append((code_segments, node))
        return nodes_

    def get_ast_objects(self, object_type, log_index = None, line_index = None, end_log_index = None, end_line_index = None):
        '''
        get AST objects within a set interval
        '''
        if log_index != None:
            try:
                start_line = self.log_to_code[str(log_index)][str(line_index)]
            except:
                return []
            if end_line_index != None and end_log_index != None:
                end_line = self.log_to_code[end_log_index][end_line_index]
            else:
                end_line = start_line
            code_interval = CodeInterval(start_line + 1, 0, end_line + 1, -1)
            nodes = self._get_relevant_ast(self.ast_, code_interval, control = True)
        else:
            nodes = ast.walk(self.ast_)
        
        nodes_ = []

        for node in nodes:
            if CodeInterval._has_segment(node) and isinstance(node, object_type):
                interval = CodeInterval.as_interval(node)
                code_segments = []
                for i in range(interval.lineno - 1, interval.end_lineno):
                    interval_ = CodeInterval(i, 0, i + 1, -1)
                    code = self._fetch_code(interval_)
                    line = self.code_to_log[i]
                    code_segments.append((line, code)) 
                nodes_.append((code_segments, node))
        
        return nodes_

# if __name__ == "__main__":
#     get_code(logs, show = True, edits = False)