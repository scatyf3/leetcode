`prev / curr / next` 三指针，逐条边掉头：先存 next，再让 `curr.next = prev`，然后两个指针同时右移。

⚠ 必须先把 `curr.next` 存下来再改它，否则链断了走不下去。返回的是 `prev`（原来的尾）。
