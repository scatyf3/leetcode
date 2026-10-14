有序 → 重复必相邻。guard + `prev`/`cur` 双指针：`prev.val == cur.val` 就删掉 cur（`prev.next = cur.next; cur = prev.next`），否则两个一起前进。

⚠ 删完 `prev` 不能动，下一个可能还是重复（`1,1,1`）；guard 的值要取题目范围外（这里 `-114`）。
