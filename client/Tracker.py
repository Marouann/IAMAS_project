from atom import Atom, DynamicAtom


class Tracker(object):
    def __init__(self, coords: '(int,int)'):
        self.reachable = set()
        self.boundary = set()  # cells that are reachable, but are curently occupied
        self.position = coords  ##tuple


    def estimate(self, state):  # estimates reachable cells
        self.reachable = set()
        frontier = set()
        self.reachable.add(self.position)
        frontier.add(self.position)

        while frontier:
            cell = frontier.pop()
            if state.find_neighbours(cell):
                for neighbour in state.find_neighbours(cell):
                    if Atom('Free', neighbour) in state.atoms and neighbour not in self.reachable:
                        self.reachable.add(neighbour)
                        frontier.add(neighbour)
                    elif neighbour not in self.reachable:
                        self.boundary.add(neighbour)

        return self.reachable

    def intersection(self, other_reachable: 'Tracker', state) -> 'int':
        '''Outputs if the two Areas are intersected'''
        if self.reachable & other_reachable.reachable:
            return 2  # if it is currently reachable
        elif other_reachable.position in self.boundary:
            return 2  # if it is currently reachable
        elif self.position in other_reachable.boundary:
            return 2  # if it is currently reachable
        elif self.boundary & other_reachable.boundary:
            return 1  # it there is exactly one oclussion on the way
        elif DynamicAtom('Distance', self.position, other_reachable.position) in state.rigid_atoms:
            return 0  # more than one occlusion
        else:  ## not reachable at all
            return -1

    # def intersection_members(self, other_reachable: 'Tracker') -> '{}':
    #    return self.reachable & other_reachable.reachable

    def boundary_members(self, other_reachable: 'Tracker') -> '{}':
        return self.boundary & other_reachable.boundary  ### coordinates of occlusions

    def boundary_atoms(self, other_reachable: 'Tracker', state) -> '{}':
        boundary_ = self.boundary_members(other_reachable)
        atoms = set()
        for coord in boundary_:

            if state.find_box(coord):
                atoms.add(state.find_box(coord))
            elif state.find_agent_by_position(coord):
                atoms.add(state.find_agent_by_position(coord))
        return atoms

    def check_if_reachable(self, coords: '(int,int)'):
        return coords in self.reachable
