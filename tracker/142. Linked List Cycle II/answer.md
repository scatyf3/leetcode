快慢指针（慢 1 快 2）从同一起点出发，相遇后把一个放回 head，两个都每次走 1 步，再相遇处就是入环点。由 `2(a+b) = a+b+n(b+c)` 得 `a = c + (n-1)(b+c)`。

⚠ 两指针必须从同一起点出发（`slow = fast = head`，或都先走一步）；`slow=head, fast=head.next` 判环没问题，但第二阶段的等式就不成立了。`fast` 和 `fast.next` 都要判空。
