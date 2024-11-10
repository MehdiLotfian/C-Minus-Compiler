"""
The Data Structure for the memory management
it should support the following operations:
    1. get_temp() : allocate a new memory block
    2. find_addr(input) : find address of the input

"""
from collections import defaultdict
class Memory():

    #DATA: {scope: {a:123, b:245}, scope2: {...} }
    def __init__(self):
        self.Data = defaultdict(dict)
        self.DataType = defaultdict(dict)
        self.functions = defaultdict(str)
        self.function_type = defaultdict(str)
        self.fun_to_addr = defaultdict(str)
        self.data_pointer = 100
        self.temp_pointer = 3100
        self.param_pointer = 1000
        self.return_pointer = 3000
        
        

    def get_temp(self):
        self.temp_pointer += 4
        return self.temp_pointer - 4
    
    def add_return_function(self, input):
        self.fun_to_addr[input] = self.return_pointer
        self.return_pointer += 4

    def get_param(self):

        self.param_pointer += 4
        return self.param_pointer - 4

    def reset_param(self):
        self.param_pointer = 1000

    def find_addr(self, input, func):
        if input in self.Data[func]:
            return self.Data[func][input]
        elif input in self.Data['global']:
             return self.Data['global'][input]           
        else:
            #Throw an error
            # print("Error: variable not found")
            return None
    def find_addr_only_scope(self, input, func):
        if input in self.Data[func]:
            return self.Data[func][input]          
        else:
            #Throw an error
            # print("Error: variable not found")
            return None    
            
    def find_type(self, input, func):
        if input in self.DataType[func]:
            return self.DataType[func][input]
        elif input in self.DataType['global']:
            return self.DataType['global'][input]
        else: 
            return None

    def add_var(self, input, func):
        self.Data[func][input] = self.data_pointer
        self.DataType[func][input] = 'var'
        self.data_pointer += 4
    
    def find_var(self, input, func):
        #loop through memroy to find the variable
        for key, value in self.Data[func].items():
            if value == input:
                return key
        for key, value in self.Data['global'].items():
            if value == input:
                return key
        return None 
    
    def get_data_type(self, input , scope):
        var = None
        for key, value in self.Data[scope].items():
            if value == input:
                var = key
                break
        if var is not None:
            return self.DataType[scope][var]
        for key, value in self.Data['global'].items():
            if value == input:
                var = key
                break
        return self.DataType['global'][var]

    def get_data_type_by_symbol(self, input, scope):
        return self.DataType[scope][input]

    def add_array(self, input, size, func, is_pointer=False):
        if input in self.Data:
            #Throw an error
            print("Error: variable already exists")
        else:
            self.Data[func][input] = self.data_pointer
            if not is_pointer:
                self.DataType[func][input] = 'array'
            else:
                self.DataType[func][input] = 'array-ptr'
            self.data_pointer += 4*size
    
    def add_function(self, input, line, type):
        self.functions[input] = line
        self.function_type[input] = type
    
    def get_function_line(self, input):
        return self.functions[input]

    def get_function_type_with_line(self, input):
        for k, v in self.functions.items():
            if v == input:
                return self.function_type[k]
            
    def get_function_name(self, input):
        for k, v in self.functions.items():
            if v == input:
                return k
            
    def get_function_return_addr(self, input):
        return self.fun_to_addr[input]