from atom import *
from state import *


class Access(object):
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

        return self.reachable

    def intersection(self, other_reachable: 'Access') -> 'bool':
        if self.reachable & other_reachable.reachable:
            return True
        else:
            return False

    def check_if_reachable(self, coords: '(int,int)'):
        return coords in self.reachable
