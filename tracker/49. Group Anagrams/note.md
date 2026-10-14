# 49. Group Anagrams

str不可变，所以不能直接dot sort 
```python
# s_key = s.sort()
s_key = key = "".join(sorted(s))
```

还有个经典 not in和dict的分类讨论

```python
if s_key not in dc:
    dc[s_key]=[s_raw]
else:
    dc[s_key].append(s_raw)
```