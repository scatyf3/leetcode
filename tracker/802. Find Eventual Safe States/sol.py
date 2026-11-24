class Solution:
    def eventualSafeNodes(self, graph: list[list[int]]) -> list[int]:
        # reverse all
        # remove non loop(+not impact by loop) is the safe path via kahn