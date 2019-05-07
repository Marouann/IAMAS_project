import sys
import math
from knowledgeBase import KnowledgeBase
from atom import *


class State:
    def __init__(self, name: 'str',
                 goals: '[dict]',
                 atoms: 'KnowledgeBase',
                 rigid_atoms: 'KnowledgeBase',
                 cost=0,
                 h_cost=0,
                 parent=None,
                 last_action={'action': 'NoOp', 'params': [], 'message': [], 'priority': 0}
                 ):
        self.name = name
        self.goals = goals
        self.helping_goals = []
        self.atoms = atoms
        self.rigid_atoms = rigid_atoms
        self.parent = parent
        self.last_action = last_action

        self.cost = cost
        self.h_cost = h_cost  # cost based on heuristics

    def remove_atom(self, atom: 'Atom'):
        self.atoms.delete(atom)

    def add_atom(self, atom: 'Atom'):
        self.atoms.update(atom)

    def contain(self, atom: 'Atom') -> 'bool':
        if atom in self.atoms:
            return True
        elif atom in self.rigid_atoms:
            return True
        else:
            return False

    def find_neighbours(self, coords: ('int', 'int')):
        neighbours = set()
        if Atom('Neighbour', coords, (coords[0] - 1, coords[1])) in self.rigid_atoms:
            neighbours.add((coords[0] - 1, coords[1]))

        if Atom('Neighbour', coords, (coords[0] + 1, coords[1])) in self.rigid_atoms:
            neighbours.add((coords[0] + 1, coords[1]))

        if Atom('Neighbour', coords, (coords[0], coords[1] - 1)) in self.rigid_atoms:
            neighbours.add((coords[0], coords[1] - 1))

        if Atom('Neighbour', coords, (coords[0], coords[1] + 1)) in self.rigid_atoms:
            neighbours.add((coords[0], coords[1] + 1))
        return neighbours

    def find_distance(self, start: ('int', 'int'), end: ('int', 'int')) -> 'int':
        if DynamicAtom('Distance', start, end) in self.rigid_atoms:
            return self.rigid_atoms[DynamicAtom('Distance', start, end)].property()[0]
        return -1

    def check_if_connected(self, start: ('int', 'int'), end: ('int', 'int')) -> 'bool':
        return DynamicAtom('Distance', start, end) in self.rigid_atoms

    def find_box(self, position):  #### WHAT DOES IT DO ??
        for atom in self.atoms:
            if atom.name == "BoxAt" and atom.variables[1] == position:
                return atom
        return False

    def find_box_position(self, box: 'str') -> ('int', 'int'):
        for atom in self.atoms:
            if atom.name == "BoxAt" and atom.variables[0] == box:
                return atom.variables[1]
        return False

    def find_box_color(self, box: 'str') -> ('str'):
        for atom in self.rigid_atoms:
            if atom.name == "Color" and atom.variables[0] == box:
                return atom.variables[1]
        return False

    def find_box_goal_distance(self, name: 'str', goal):
        boxAtom = Atom
        for atom in self.atoms:
            if atom.name == "BoxAt" and atom.variables[0] == name:
                boxAtom = atom
                break
        distance = self.find_distance(boxAtom.variables[1], goal["position"])
        return distance

    def find_box_letter(self, box_name: 'str'):  ##### WHAT DOES IT DO?
        for atom in self.rigid_atoms:
            if atom.name == "Letter" and atom.variables[0] == box_name:
                return atom

    def find_agent(self, agt: 'str'):
        for atom in self.atoms:
            if atom.name == "AgentAt" and atom.variables[0] == agt:
                return atom.variables[1]

    def find_agent_by_position(self, position):  #### WHAT DOES IT DO ??
        for atom in self.atoms:
            if atom.name == "AgentAt" and atom.variables[1] == position:
                return atom
        return False

    def find_object_at_position(self, position: ('int', 'int')) -> 'Atom':
        for atom in self.atoms:
            if atom.name == "AgentAt" and atom.variables[1] == position:
                return atom
            elif atom.name == "BoxAt" and atom.variables[1] == position:
                return atom
        return False

    def get_unmet_goals(self):
        metGoals = []
        unmetGoals = []
        for goal in self.goals:
            box = self.find_box(goal['position'])
            if False == box:
                unmetGoals.append(goal)
            else:
                boxLetter = self.find_box_letter(box.variables[0])
                letter = boxLetter.variables[1]
                if letter != goal['letter']:
                    unmetGoals.append(goal)
                else:
                    metGoals.append(goal)
        return [unmetGoals, metGoals]

    def getNeithbourGoals(self, position):
        neighbourLocations = []
        for atom in self.rigid_atoms:
            if atom.name == "Neighbour" and position == atom.variables[0]:
                neighbourLocations.append(atom.variables[1])

        neighbourGoals = []
        for atom in self.rigid_atoms:
            if atom.name == "GoalAt":
                for location in neighbourLocations:
                    if location == atom.variables[1]:
                        neighbourGoals.append(atom)

        return neighbourGoals

    def getNeithbourFieldsWithoutGoals(self, position):
        neighbourLocations = []
        for atom in self.rigid_atoms:
            if atom.name == "Neighbour" and position == atom.variables[0]:
                neighbourLocations.append(atom.variables[1])

        result = neighbourLocations

        for atom in self.rigid_atoms:
            if atom.name == "GoalAt":
                for location in neighbourLocations:
                    if location == atom.variables[1]:
                        result.remove(location)

        return result

    def copy(self):
        atoms_copy = KnowledgeBase("Atoms")
        atoms_copy.copy(self.atoms)
        return State(name=self.name,
                     goals=self.goals,
                     atoms=atoms_copy,
                     rigid_atoms=self.rigid_atoms,
                     parent=self.parent,
                     cost=self.cost)

    def create_child(self, action, cost=0, h_cost=0):
        atoms_copy = KnowledgeBase("Atoms")
        atoms_copy.copy(self.atoms)

        state = State(name=self.name,
                      goals=self.goals,
                      atoms=atoms_copy,
                      rigid_atoms=self.rigid_atoms,
                      parent=self,
                      cost=self.cost + cost,
                      h_cost=h_cost)
        state.last_action = {'action': action[0], 'params': action[1], 'message': action[2], 'priority': action[4]}
        action[0].execute(state, action[1])
        return state

    def atoms(self):
        return self.atoms + self.rigid_atoms

    ############################
    ##Private or implicit methods

    def __total_cost__(self) -> 'int':
        return (self.cost + self.h_cost, self.last_action['priority'])

    def __eq__(self, other: 'State'):
        return self.atoms == other.atoms  # and self.parent == other.parent and self.last_action == other.last_action

    def __str__(self):
        state_str = "State " + self.name + "\n"
        state_str += str(self.rigid_atoms)
        state_str += str(self.atoms)

        return (state_str)

    def __hash__(self):
        return hash(self.atoms)

    def __cmp__(self, other: 'State'):
        if self.__total_cost__() > other.__total_cost__():
            return 1
        elif self.__total_cost__() == other.__total_cost__():
            return 0
        elif self.__total_cost__() < other.__total_cost__():
            return -1

    def __lt__(self, other: 'State'):
        return self.__total_cost__() < other.__total_cost__()

    def __gt__(self, other: 'State'):
        return self.__total_cost__() > other.__total_cost__()
