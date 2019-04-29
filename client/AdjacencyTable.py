from state import State
import numpy as np
from atom import Atom, DistanceAtom
from knowledgeBase import KnowledgeBase
from heapq import heapify, heappush, heappop


def level_adjacency(state: 'State', row: 'int', col: 'int'):
    '''Calculates real distances between cells in a level'''
    def distance_calculator(start: ('int', 'int'), end: ('int', 'int')) -> 'int':
        frontier = list()
        explored = set()
        for neighbour in state.find_neighbours(start):
            heappush(frontier, (1, neighbour))

        while frontier:
            current = heappop(frontier)
            explored.add(current[1])
            if current[1] == end:
                return current[0]
            elif state.find_neighbours(current[1]):
                for neighbour in state.find_neighbours(current[1]):
                    if neighbour not in explored:
                        heappush(frontier, (current[0] + 1, neighbour))
                        explored.add(neighbour)
                heapify(frontier)
        return -1 ##if none is found it returns negative value

    adjacency = KnowledgeBase('Real Distances')
    for r in range(row):
        for c in range(col):
            for r1 in range(row):
                for c1 in range(col):
                    distance = distance_calculator((r, c), (r1, c1))
                    if distance > 0 and not (r == r1 and c == c1):
                        adjacency.update(Atom('Distance', (r, c), (r1, c1), distance))
    return adjacency
