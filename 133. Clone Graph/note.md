怎么想到visited，即建立old node和new node对应的hash table？我完全想不到
但是visited一般用set，为啥用hash table，好像同时解决了找start node和visit的问题，如何想到，用一个guard节点和set按道理也行吗

一句话总结：set 回答「有没有」，dict 回答「有没有 + 是什么」。visited 的经典用法只需要前者，这题需要后者。
visited的不是必被clone吗

No dfs里visit是不是可以还没被clone，正在等待clone
visited 里的节点克隆对象一定已经存在（visited[old] = new 写在 Node(old.val) 之后），但那个克隆可能还没填完

所以实际有三种状态，不是两种：

状态	在 visited 里	克隆对象	含义
白：没碰过	否	不存在	—
灰：正在处理	是	存在但 neighbors 没填完	还在递归栈上
黑：处理完	是	完整	dfs 已返回

为啥不适合bfs来着