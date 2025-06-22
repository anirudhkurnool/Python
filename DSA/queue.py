class Queue:
    def __init__(self):
        self.arr = []
        self.size = 0 

    def __str__(self):
        return f"=====QUEUE=====\nsize : {self.size}\n{self.arr}"

    def __repr__(self):
        return f"=====QUEUE=====\nsize : {self.size}\n{self.arr}"

    def enqueue(self, new_element):
        self.arr.append(new_element)
        self.size += 1
    
    def dequeue(self):
        if self.size == 0:
            raise OverflowError("queue is empty")
        
        self.size -= 1
        return self.arr.pop(0)

    def peek(self):
        if self.size == 0:
            raise OverflowError("queue is empty")
        
        return self.arr[0]