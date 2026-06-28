'''
traveling recall, order of city you visited, but you only have flight ticket, but you do not known the order
reconstruct the order of cities you visited based on the flight tickets you have.
input: list of tickets
output: travel sequence of cities you visited

Clarify
do not assume anything

for simplicity, no loop in the trip

input: [[A,B],[B,C]]
output: [A,B,C]

like () matching: maybe using stack?: but input with out order
hashmap?
for each input, use store each dst as key, for each interated element, check current trip[0] is in hash table

hash: dst:src
no, dst:list is better
we need somehow store both start and end=> 2 way linkedlist, 
but we are in python, just costumized some class to process this
'''

class Slice():
    def __init__(self,lst):
        self.start=lst[0]
        self.end=lst[len(lst)-1]
        self.lst=lst
    def add_tail(self,dst):
        self.lst.append(dst)
        self.end=dst
    def add_prev(self,src):
        self.lst.insert(0,src)
        self.start=src
    def __repr__(self):
        return f"start={self.start},end={self.end},lst={self.lst}"
        
def solution(trips):
    c = [] # list of slices
    c_hit=0
    for ticket in trips:
        src=ticket[0]
        dst=ticket[1]
        # find, can be more effient cache, but currently we use simple loop
        # ie use hash(src,dst) as hashmap's key
        for slice in c:
            if dst == slice.start: 
                print("find prefix")
                slice.add_prev(src)
                c_hit=1
            elif src == slice.end:
                print("find suffix")
                slice.add_tail(dst)
                c_hit=1
        if(c_hit==0):
            # cannot put current tick into sequence, just put in cache and wait for further process
            slice = Slice(ticket)
            c.append(slice)
        print(c)
    # check if trip is valid
    if(len(c)==1): # valid, only have one route
        return c[0].lst
    else:
        # not valid, error processing
        return []
    
'''
how to process loop/round trip?
loop: returned sequence might be random started
just add elif to cache search, avoid hit both prefix and suffix

round trip
[[A,B],[B,A]]
'''
# naive
trips=[['A','B'],['B','C']]
print(solution(trips))

# round
trips=[['A','B'],['B','A']]
print(solution(trips))


    