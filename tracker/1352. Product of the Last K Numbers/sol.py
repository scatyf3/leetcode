class ProductOfNumbers:

    def __init__(self):
        self.prefix_mul = [1]
        self.start_zero = False
        # self.zero_index = set()

    def add(self, num: int) -> None:
        if num!=0:
            if self.prefix_mul:
                self.prefix_mul.append(self.prefix_mul[-1]*num)
            else:
                self.prefix_mul.append(num)
        else:
            self.prefix_mul=[1] # reset
            self.start_zero = True


    def getProduct(self, k: int) -> int:
        start = max(len(self.prefix_mul)-k-1,-1)
        # print(start,self.prefix_mul)
        if start==-1 and self.start_zero:
            return 0
        return self.prefix_mul[-1]//self.prefix_mul[start]