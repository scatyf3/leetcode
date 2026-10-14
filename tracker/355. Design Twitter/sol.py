class Twitter:
    '''
    for each user, we maintain a heap record it's tweet by time order
    for a general timeline, we maintain another heap to record my follow user's most recent tweet?(or array)
    '''

    def __init__(self):
        self.followlist={} # self id:set of following ids
        self.userlist={} # user id-user list
        self.timestamp=0
        

    def postTweet(self, userId: int, tweetId: int) -> None:
        if userId in self.userlist:
            self.userlist[userId].append((self.timestamp, tweetId))
        else:
            self.userlist[userId]=[(self.timestamp, tweetId)]
        self.timestamp+=1
        

    def getNewsFeed(self, userId: int) -> List[int]:
        h = []
        for userid in self.userlist:
            if userid == userId or userid in self.followlist.get(userId, set()): # avoid error
            # if userid == userId or userid in self.followlist[userId]
                for time, twid in self.userlist[userid]:
                    heapq.heappush(h, (-time, twid))
        res = []
        while h and len(res) < 10:
            _, twid = heapq.heappop(h)
            res.append(twid)
        return res


    def follow(self, followerId: int, followeeId: int) -> None:
        if followerId not in self.followlist:
            self.followlist[followerId]=set()
        self.followlist[followerId].add(followeeId)
        

    def unfollow(self, followerId: int, followeeId: int) -> None:
        if followerId in self.followlist:
            self.followlist[followerId].discard(followeeId) # .remove(followeeId)
        


'''
我的直觉1. 用户推特用heap 2. 每个用户最新的tweet用heap

agent1. post tweet天生time order，list就够了
'''