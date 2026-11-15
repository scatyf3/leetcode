class Solution:
    def maximumSwap(self, num: int) -> int:
        num_lst = [int(c) for c in str(num)]
        orignal = num_lst.copy()
        pairs = sorted(enumerate(num_lst), key=lambda x: x[1], reverse=True)

        for idx in range(len(pairs)):
            if pairs[idx][1] != orignal[idx]:
                # 同 value 取最靠后的：往后 skip 相同的 value
                k = idx
                while k + 1 < len(pairs) and pairs[k + 1][1] == pairs[idx][1]:
                    k += 1
                j = pairs[k][0]
                orignal[idx], orignal[j] = orignal[j], orignal[idx]
                break

        return int(''.join(map(str, orignal)))
