双指针各自走完自己再走对方：两人都走 `a + b + c` 步，必在交点相遇；无交点就同时走到 `None`。`curA = curA.next if curA else headB`。

⚠ `None is None` 也成立，无交点时两人同步变 None 自然退出，不用 swap 标记和特判。
