from atom import *
from state import *


class Tracker(object):
    def __init__(self, coords: '(int,int)'):
        self.reachable = set()
        self.current_cell = coords  ##tuple
        # self.estimate(state)

    def estimate(self, state: 'State', for_agent=False):  # estimates reachable cells
        self.reachable = set()
        frontier = set()
        self.reachable.add(self.current_cell)
        frontier.add(self.current_cell)

        while frontier:
            cell = frontier.pop()
            for neighbour in state.find_neighbours(cell):
                if Atom('Free', neighbour) in state.atoms and neighbour not in self.reachable:
                    self.reachable.add(neighbour)
                    frontier.add(neighbour)

                ##elif Atom('')
                 ### there is one issue with boxes and agents

        return self.reachable

    def intersection(self, other_reachable: 'Tracker') -> 'bool':
        if self.reachable & other_reachable.reachable:
            return True
        else:
            return False

    def intersection_members(self, other_reachable: 'Tracker') -> '{}':
        return self.reachable & other_reachable.reachable

    def check_if_reachable(self, coords: '(int,int)'):
        return coords in self.reachable
