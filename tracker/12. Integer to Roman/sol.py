class Solution:
    def intToRoman(self, num: int) -> str:
        # take 4 and 9 as special case
        cand = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        cand_map = {
            1000: "M",
            900: "CM",
            500: "D",
            400: "CD",
            100: "C",
            90: "XC",
            50: "L",
            40: "XL",
            10: "X",
            9: "IX",
            5: "V",
            4: "IV",
            1: "I",
        }
        res = []
        while num > 0:
            for elem in cand:
                if num-elem>=0:
                    num=num-elem
                    res.append(cand_map[elem])
                    break
            #print(num)
            #print(res)
        return "".join(res)





