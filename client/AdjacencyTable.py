from state import State
from atom import Atom, DistanceAtom
from knowledgeBase import KnowledgeBase
from heapq import heapify, heappush, heappop

def level_adjacency(state:'State', row: 'int', col: 'int'):
    def distance_calculator(start: ('int', 'int'), end:('int', 'int') ) -> 'int':
        frontier = list()
        for neighbour in state.find_neighbours(start):
            heappush(frontier, (0, neighbour))
        while frontier:
            distance = frontier[0].
            if end in frontier:
                return


        return Atom('')

    adjacency = KnowledgeBase('Real Distances')
    for r in range(row):
        for c in range(col):
            adjacency += distance_calculator(r,c)



class PrioritySet(object):
    def __init__(self):
        self.heap = []
        self.set = set()

    def add(self, d, pri):
        if not d in self.set:
            heappush(self.heap, (pri, d))
            self.set.add(d)


    def get(self):
        pri, d = heappop(self.heap)
        self.set.remove(d)
        return d

