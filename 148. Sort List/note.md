# 148. Sort List

### pass2

```python
        while fast and fast.next: # 如果只用fast，无限循环
            slow = slow.next
            fast = fast.next.next
```

必须这样写 - 规律是：一次走几步，就要守住前面几个指针。走两步，就守 fast 和 fast.next。

之前一个做法是外侧while fast，内部if fast.next再更新fast，这样会死循环...

### pass1

标准的归并排序，但感觉对咋写完全不熟悉，思路没问题，让agent给个template填空...

而且这玩意算是linkedlist里重要的题，包括快慢指针，找中点，merge之类的

## 思路

1. basecase是当前head是空，或者只有一个node
2. 快慢指针把当前表格分割两半，递归调用
3. merge递归调用返回的两个head
4. 记得用dummy


## 语法细节

1. 快慢指针，从`slow, fast = head, head.next` 这个状态比较好，这样fast在中点/中间的缝的左边，好操作
2. merge俩linkedlist，这里尺寸不保证最后剩下的一定是左或者右，有个简单的语法`cur.next = left if left else right`

## 踩坑

1. `mid = slow` → 应该是 `mid = slow.next`,**断开之前先存右半边的头**。写成 `slow` 的话右半边整段丢失,`slow` 同时出现在两半里,merge 时自己接自己成环
2. 收尾 `cur.next = right.next` → 应该是 `cur.next = left or right`。循环退出时至少一条已空,剩下那条整段有序,直接接上;`.next` 会跳过一个节点,而且 right 为 None 时直接炸
3. 找中点用 `fast = head.next`(落左中点),n=2 才切得开。见 [linked-list-template.md](../notes/linked-list-template.md) 第 1 节
