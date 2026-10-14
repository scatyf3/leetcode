# 标准版一个node一个字符；压缩版一个node多个字符，需要split

class TrieNode:
    def __init__(self):
        self.children = {}      # char -> TrieNode，一个字符一条边
        self.is_end = False     # 有没有单词恰好在这里结束

class Trie:

    def __init__(self):
        self.root = TrieNode()        # 空的哨兵节点，不存任何字符

    def insert(self, word: str) -> None:
        node = self.root
        for c in word:
            if c not in node.children:
                node.children[c]=TrieNode()             # 没有这条边就新建
            node = node.children[c]         # 沿着边走下去
        node.is_end=True                    # 走完整个 word 之后要标记什么？

    def _walk(self, s: str):
        """沿着 s 一个字符一个字符往下走：走通了返回最后一个节点，中途断了返回 None"""
        node = self.root
        for c in s:
            if c not in node.children:
                return None
            node = node.children[c]
        return node

    def search(self, word: str) -> bool:
        node = self._walk(word)
        return bool(node and node.is_end)

    def startsWith(self, prefix: str) -> bool:
        node = self._walk(prefix)
        return bool(node)
