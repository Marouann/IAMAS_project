from state import State
from atom import DynamicAtom
from knowledgeBase import KnowledgeBase
from heapq import heapify, heappush, heappop


def level_adjacency(state: 'State', row: 'int', col: 'int') -> 'KnowledgeBase':
    '''Calculates real distances between cells in a level'''
    def distance_calculator(coord: ('int', 'int')):
        frontier = list()
        explored = set()
        memory = list()
        for neighbour in state.find_neighbours(coord):
            heappush(frontier, (1, neighbour))

        while frontier:
            heapify(frontier)
            current = heappop(frontier)
            explored.add(current[1])
            memory.append(current)

            if state.find_neighbours(current[1]):
                for neighbour in state.find_neighbours(current[1]):
                    if neighbour not in explored:
                        heappush(frontier, (current[0] + 1, neighbour))
                        explored.add(neighbour)
                        memory.append((current[0] + 1, neighbour))
        return memory

    adjacency = KnowledgeBase('Real Distances')

    for r in range(row):
        for c in range(col):
            result = distance_calculator((r, c))
            for distance, cell in result:
                atom = DynamicAtom('Distance', (r, c), cell, )
                atom.assign_property(distance)
                adjacency.update(atom)
    return adjacency
