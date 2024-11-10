from codegen.memory import Memory
from codegen.semantic_stack import semantic_stack
from codegen.program_block import ProgramBlock


class CodeGenerator:
    def __init__(self):
        self.ss = semantic_stack()
        self.pb = ProgramBlock()
        self.memory = Memory()
        self.loop_stack = []
        self.semantic_errors = []
        self.scope = 'global'
        self.dummy = False
        self.dummy_line = 0
        self.actions = ['PNUM', 'PUSH_TYPE', 'PID', 'VAR_DEC', 'ARR_ACC', 'LABEL', 'UNTIL', 'BREAK', 'PID_DEC', 'FUN_DEC', 'VAR_DEC_PARAM',
         'ASSIGN', 'PUSHOP', 'ADD_SUB', 'OUTPUT', 'MUL', 'CMP', 'ARRAY_DEC', 'SAVE', 'JPF_SAVE', 'INIT_RETURN', 'DEL_TMP',
         'JP', 'PUSH_ASSIGN','BREAK','ARR_DEC_PARAM', 'RETURN', 'FUN_END','RETURN_VOID', 'ASSIGN_ARG', 'FUN_END_CALL', 'POP_STACK']
         
        self.fun_dec_signal = (False, 0)
    
    def run(self, type, current_token, current_line):
        #print("Code Gen executed")
        print(current_line)
        if current_token == 'global':
            print('hi')
        if current_line != self.dummy_line:
            self.dummy = False
        if self.dummy:
            return
        print(f'type: {type}, current_token: {current_token}')
        if type == 'POP_STACK':
            if current_token.isnumeric():
                self.dummy = True
                self.dummy_line = current_line
        elif type == 'PNUM':
            number = current_token
            t = self.memory.get_temp()
            self.pb.add_code('ASSIGN', f'#{number}', f'{t}')
            self.ss.push(t)
        elif type == 'PUSH_TYPE':
            data_type = current_token
            self.ss.push(data_type)
        elif type == 'PID':
            id = current_token
            addr = self.memory.find_addr(id, self.scope)
            if addr is None:
                addr = self.memory.get_function_line(id)
            if addr is None:
                self.ss.push('SEMANTIC PID')
                return
            self.ss.push(addr)
        elif type == 'PID_DEC':
            id = current_token
            addr = self.memory.find_addr_only_scope(id, self.scope)
            id = addr if addr is not None else id
            self.ss.push(id)
        elif type == 'VAR_DEC':
            data_type = self.ss.get_top(1)
            ## soomantic
            if data_type != 'int':
                self.semantic_errors.append(f'#{current_line}: Semantic Error! Illegal type of void for \'{self.ss.get_top()}\'.')
                self.ss.pop(1)
                return                               
            ## end soomantic
            id = self.ss.get_top()
            self.memory.add_var(id, self.scope)
            id = self.memory.find_addr(id, self.scope)
            self.ss.pop(2)
            self.pb.add_code('ASSIGN', f'#0', f'{id}')  
        elif type == 'FUN_DEC':
            data_type = self.ss.get_top(1)
            self.scope = self.ss.get_top()
            self.memory.add_return_function(self.scope)
            if self.scope == 'main':
                self.pb.set_instruction(0, 'JP', self.pb.get_line())

            if data_type != 'int':
                self.memory.add_function(self.scope, self.pb.get_line(), 'void')
                self.ss.pop(1)
            else:   
                self.memory.add_function(self.scope, self.pb.get_line(), 'int')                           
                id = self.ss.get_top()
                self.ss.pop(2)  


        elif type == 'ARRAY_DEC':
            data_type = self.ss.get_top(1)   
            id = self.ss.get_top()
            self.memory.add_array(id, int(current_token), self.scope)
            id = self.memory.find_addr(id, self.scope)
            self.ss.pop(2)
            self.pb.add_code('ASSIGN', f'#0', f'{id}') 

        elif type == 'ARR_DEC_PARAM':
            data_type = self.ss.get_top(1)   
            id = self.ss.get_top()
            self.ss.pop(2)
            self.memory.add_array(id, 1, self.scope, True)
            idx = self.memory.find_addr(id, self.scope)
            self.pb.add_code('ASSIGN', f'{self.memory.get_param()}', f'{idx}')

        elif type == 'VAR_DEC_PARAM':
            data_type = self.ss.get_top(1)   
            id = self.ss.get_top()
            self.ss.pop(2)
            self.memory.add_var(id, self.scope)
            idx = self.memory.find_addr(id, self.scope)
            self.pb.add_code('ASSIGN', f'{self.memory.get_param()}', f'{idx}')
        elif type == 'FUN_END':
            self.memory.reset_param()
            
        elif type == 'ASSIGN':
            to_id = self.ss.get_top(2)
            op = self.ss.get_top(3)
            from_id = self.ss.get_top()
            self.ss.pop(3)
            self.pb.add_code('ASSIGN', f'{from_id}', f'{to_id}') 
            if op == '=':
                self.ss.push(from_id)
        elif type == 'PUSH_ASSIGN':
            self.ss.push(current_token)     
        elif type == 'PUSHOP':
            operation = current_token
            if operation == "+":
                operation = 'ADD'
            elif operation == '-':
                operation = 'SUB'
            elif operation == '<':
                operation = 'LT'
            elif operation == '==':
                operation = 'EQ'
            else:
                print(f'wtf is this: {operation}')
            self.ss.push(operation)
        elif type == 'ADD_SUB':
            id1 = self.ss.get_top(2)
            operation = self.ss.get_top(1)
            id2 = self.ss.get_top()
            self.ss.pop(3)
            if self.memory.find_type(self.memory.find_var(id1, self.scope), self.scope) == 'array':
                self.semantic_errors.append(f'#{current_line}: Semantic Error! Type mismatch in operands, Got array instead of int.')
                self.ss.push("SEMANTIC SUB_ADD")
                return
            if self.memory.find_type(self.memory.find_var(id2, self.scope), self.scope) == 'array':
                self.semantic_errors.append(f'#{current_line}: Semantic Error! Type mismatch in operands, Got array instead of int.')
                self.ss.push("SEMANTIC SUB_ADD")
                return
            t = self.memory.get_temp()
            self.pb.add_code(operation, f'{id1}', f'{id2}', f'{t}')  
            self.ss.push(t)
        elif type == 'MUL':
            id1 = self.ss.get_top()
            id2 = self.ss.get_top(1)
            self.ss.pop(2)
            t = self.memory.get_temp()
            self.pb.add_code('MULT', f'{id1}', f'{id2}', f'{t}')
            self.ss.push(t)
        elif type == 'CMP':
            id1 = self.ss.get_top(2)
            id2 = self.ss.get_top(0)
            operation = self.ss.get_top(1)
            self.ss.pop(3)
            t = self.memory.get_temp()
            self.pb.add_code(operation, f'{id1}', f'{id2}', f'{t}')
            self.ss.push(t)
        elif type == 'ARR_ACC':
            symbol = self.ss.get_top(1)
            idx = self.ss.get_top()
            self.ss.pop(2)
            t = self.memory.get_temp()
            self.pb.add_code("MULT", f'{idx}', f'#4', f'{t}')
            datatype = self.memory.get_data_type(symbol, self.scope)
            if datatype == 'array':
                self.pb.add_code("ADD", f'{t}', f'#{symbol}', f'{t}')
            else:
                self.pb.add_code("ADD", f'{t}', f'{symbol}', f'{t}')
            self.ss.push(f'@{t}')
        elif type == 'LABEL':
            idx = self.pb.get_line()
            self.ss.push(idx)
        elif type == 'BREAK':
            idx = self.pb.add_empty_block()
            self.loop_stack.append(idx)
        elif type == 'UNTIL':
            cond = self.ss.get_top()
            idx = self.ss.get_top(1)
            self.ss.pop(2)
            self.pb.add_code('JPF', f'{cond}', f'{idx}')
            if len(self.loop_stack) > 0:
                idx = self.loop_stack.pop()
                self.pb.set_instruction(idx,'JP', f'{self.pb.get_line()}')
        elif type == 'SAVE':
            idx = self.pb.add_empty_block()
            self.ss.push(idx)
        elif type == 'JPF_SAVE': #SAVE #JPF
            idx = self.ss.get_top()
            cond = self.ss.get_top(1)
            self.ss.pop(2)
            i = self.pb.get_line()
            self.ss.push(i)
            self.pb.add_empty_block()
            self.pb.set_instruction(idx, 'JPF', f'{cond}', f'{i + 1}')
        elif type == 'JP':
            idx = self.ss.get_top()
            i = self.pb.get_line()
            self.pb.set_instruction(idx, 'JP', f'{i}')
            self.ss.pop()
        elif type == 'OUTPUT':
            t = self.ss.get_top()
            self.ss.pop(1)
            self.pb.add_code('PRINT', f'{t}')
        elif type == 'RETURN':
            id = self.ss.get_top()
            t = self.ss.pop()
            self.pb.add_code("ASSIGN", f'{id}', f'{2000}')
            
            self.pb.add_code("JP", f'@{self.memory.get_function_return_addr(self.scope)}')
        elif type == 'RETURN_VOID':
            self.pb.add_code("JP", f'@{self.memory.get_function_return_addr(self.scope)}')
        elif type == 'ASSIGN_ARG':
            id = self.ss.get_top()
            param_addr = self.memory.get_param()
            dtype = None
            try:
                dtype = self.memory.get_data_type(id, self.scope)
            except:
                pass
            if dtype == 'array':
                self.pb.add_code('ASSIGN', f'#{id}', param_addr)
            elif dtype == 'array-ptr':
                self.pb.add_code('ASSIGN', f'{id}', param_addr)
            else:
                self.pb.add_code('ASSIGN', id, param_addr)
            self.ss.pop()
        elif type == 'FUN_END_CALL':
            self.memory.reset_param()
            fun_addr = self.ss.get_top()
            self.ss.pop()
            fun_name = self.memory.get_function_name(fun_addr)
            fun_return_addr = self.memory.get_function_return_addr(fun_name)
            self.pb.add_code('ASSIGN', '#' + str(self.pb.get_line() + 2), f'{fun_return_addr}')
            self.pb.add_code('JP', str(fun_addr))
            temp = self.memory.get_temp()
            func_ret = self.memory.get_function_type_with_line(fun_addr)
            if func_ret == 'int':
                self.pb.add_code('ASSIGN', '2000', f'{temp}')
                self.ss.push(temp)
        elif type == 'DEL_TMP':
            try:
                tmp = int(self.ss.get_top())
                if tmp >= 3100:
                    self.ss.pop()
            except:
                pass
                

        print(f'{self.memory.param_pointer}'.center(100,'-'))
        print(f'stack: {self.ss.stack}')
        self.pb.print_block()
        print("************************************"*10)

    def get_printed_code(self):
        out_str = ''
        for i, line in enumerate(self.pb.codes):
            if line is None:
                break
            out_str += f'{i}\t{line}\n'
        return out_str
