class MinStack:

    def __init__(self):
        self.lst = []
        self.minstk = [] # all ops are O(1)

    def push(self, value: int) -> None:
        if len(self.lst)>0:
            self.minstk.append(min(self.minstk[-1],value))
        else:
            self.minstk.append(value)
        self.lst.append(value)
        
    def pop(self) -> None:
        self.minstk.pop()
        return self.lst.pop()
        

    def top(self) -> int:
        return self.lst[-1]
        

    def getMin(self) -> int:
        # print(self.minstk)
        return self.minstk[-1]
        
