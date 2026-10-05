这道题感觉很难啊，这里的key是找旋转点
```python
        # 1. [l:start] > [start:r]
        # 其实二分的l和r value不会被用到
        while l<=r:
            if nums[mid]>=nums[0]:
                l=mid+1
            else:
                r=mid-1
            mid = (l+r)//2
        
```

无论是正常binary，还是这种变体，我们不会用到l和r对应的value，这样的话要处理跳变点
0. 我们找的是跳变缝
1. 直接比和左边第一个就能判断在哪里
2. 递增数列二分我们只比mid value和target
