class ProgramBlock:
    
    def __init__(self):
        self.codes = [None] * 2000
        self.line = 0
        
    def add_code(self, opcode, oper1='', oper2='', oper3=''):
        self.codes[self.line] = f"({opcode}, {oper1}, {oper2}, {oper3})"
        self.line += 1

    def set_instruction(self, index, opcode, oper1='', oper2='', oper3=''):
        print(index, opcode, oper1, oper2, oper3)
        self.codes[index] = f"({opcode}, {oper1}, {oper2}, {oper3})"

    def add_empty_block(self):
        self.line += 1
        return self.line - 1
    
    def get_line(self):
        return self.line

    def print_block(self):
        for i in range(self.line):
            print(self.codes[i])

