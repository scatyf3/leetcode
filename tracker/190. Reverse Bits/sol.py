class Solution:
    def reverseBits(self, n: int) -> int:
        bits = deque()
        CNT=32
        while n>0:
            bits.appendleft(n%2)
            n=n//2
        while len(bits)<32:
            bits.appendleft(0)
        # print(bits) #reverse order list
        while CNT>0:
            cur = bits.popleft()
            bits.append(cur)
            CNT-=1
        p=1
        res=0
        for bit in bits:
            res+=bit*p
            p=2*p
        return res

