class semantic_stack:
    """
    The semantic stack for pushing and poping the semantic values
    """
    def __init__(self):
        self.stack = []
        self.size = 0


    def push(self, item):
        self.size += 1
        self.stack.append(item)

    def pop(self, i = 1):
        if self.size == 0:
            print("Error: stack underflow")
            return None
        else:
            self.size -= i
            for j in range(i):
                self.stack.pop()
    
    def get_top(self, i=0):
        if self.size - i <= 0:
            print("Error: stack underflow")
            return None
        else:
            return self.stack[-1-i]
