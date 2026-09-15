class Solution:
    def nextGreatestLetter(self, letters: List[str], target: str) -> str:
        '''
        ["c","f","j"]
          F.  F.  F
        ["c","f","j"]
          T.  F.  F

          条件是>，找右缝
        '''

        l=0
        r=len(letters)-1
        mid=(l+r)//2
        while(l<=r):
            if letters[mid]>target: #T
                r=mid-1
            else:
                l=mid+1
            mid=(l+r)//2
        if l>=len(letters):
            return letters[0]
        else:
            return letters[l]