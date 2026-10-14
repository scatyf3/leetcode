dummy + `group_prev`（上一组尾巴）：先走 k 步找 `kth`，不够 k 个直接返回；反转这一组时 `prev` 初值设成 `group_next = kth.next`，反完尾巴自动接上下一组；再 `group_prev.next = kth`，`group_prev` 挪到旧头。

⚠ 自己那版用数组存每组 start/end、最后统一连线，极易连出环。`group_next` 要在反转前先存，反转会改掉 `kth.next`。
