class Stack:
    def __init__(self):
        self.arr = []
        self.size = 0 

    def __repr__(self):
        return f"=====STACK=====\nsize : {self.size}\n{self.arr}"
    
    def __str__(self):
        return f"=====STACK=====\nsize : {self.size}\n{self.arr}"

    def push(self, new_element):
        self.arr.append(new_element)
        self.size += 1

    def pop(self):
        if self.size == 0:
            raise OverflowError("stack is empty")
        self.size -= 1
        return self.arr.pop()

    def peek(self):
        if self.size == 0:
            raise OverflowError("stack is empty")
        return self.arr[-1]