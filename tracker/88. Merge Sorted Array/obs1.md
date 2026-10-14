
1. tail case for remaining array, I forget it during first round
2. read ability, I wrongly understand the m's meaning, which is the nums1 actual bound instead of it's real capacity => need a sop to summarize every varible and it's meaning
3. suboptimal, I copy the nums1 for mindset simplicity, but interviewer should ask an inplace version...seen in `opt2.py`


me: what's the this trick's name, is there any other problem using this trick
AI: The trick is usually called "two pointers from the end" / backward (reverse) two-pointer fill, or more specifically in-place merge from the back. The key idea has a name worth remembering: write from the back to avoid overwriting unread data — sometimes called the "fill from the end" / suffix-filling technique.
Practical advice: For high-frequency "Easy" problems like this, there is no need to strive for the optimal solution on your first attempt—simply memorizing the approach is sufficient. It is the Medium and Hard problems that truly test your problem-solving skills

me: really, remember these trick is meaningless, irl if we want to merge something, we can just allocate an tmp buffer.  If resource is limited, wen can write an memory pool do this proxied allocation for us and offload our mindset bindwidth. What's the point of this optimization?
AI do not answer meaningful thing...


