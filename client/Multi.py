import sys
from state import State
from atom import Atom, DynamicAtom
from knowledgeBase import KnowledgeBase
from heapq import heapify, heappush, heappop
from multiprocessing import Process, Manager

def multiprocess_adjacency(state: 'State', num_processes= 1):
    adjacency = KnowledgeBase('Real Distances')
    with Manager() as manager:
        result = manager.list() # <-- can be shared between processes.
        processes = []
        interval = int(30/num_processes)
        for i in range(num_processes):
            lower = i* interval
            upper = lower + interval
            p = Process(target=adjacency_calculator, args=(result,state ,lower, upper))  # Passing the list
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        for start, end, distance in result:
            atom = DynamicAtom('Distance', start, end )
            atom.assign_property(distance)
            adjacency.update(atom)

    return adjacency

def adjacency_calculator(shared_list, state, lower_limit, upper_limit):
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

    for r in range(lower_limit, upper_limit):
        for c in range(0,30):
            result = distance_calculator((r,c))
            for distance,  cell in result :
                shared_list.append([(r,c), cell, distance])