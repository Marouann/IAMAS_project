from atom import Atom, DynamicAtom


class Tracker(object):
    def __init__(self, coords: '(int,int)'):
        self.reachable = set()
        self.boundary = set()  # cells that are reachable, but are curently occupied
        self.current_cell = coords  ##tuple
        # self.estimate(state)

    def estimate(self, state):  # estimates reachable cells
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

                else:
                    self.boundary.add(neighbour)

        return self.reachable

    def intersection(self, other_reachable: 'Tracker') -> 'int':
        if self.reachable & other_reachable.reachable:
            return 1  # if it is currently reachable
        elif self.boundary & other_reachable.boundary:
            return 0  # it there is an occlusion
        else:  # not reachable or more than one occlusion
            return -1

    def intersection_members(self, other_reachable: 'Tracker') -> '{}':
        return self.reachable & other_reachable.reachable

    def check_if_reachable(self, coords: '(int,int)'):
        return coords in self.reachable
