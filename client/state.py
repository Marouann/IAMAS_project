import sys
import math
from knowledgeBase import KnowledgeBase
from atom import *
import numpy as np


class State:
    def __init__(self, name: 'str',
                 goals: '[dict]',
                 atoms: 'KnowledgeBase',
                 rigid_atoms: 'KnowledgeBase',
                 cost=0.0,
                 h_cost=0.0,
                 parent=None,
                 last_action={'action': 'NoOp', 'params': [], 'message': ['NoOp'], 'priority': 0.7}
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
        if StaticAtom('Distance', start, end) in self.rigid_atoms:
            return self.rigid_atoms[StaticAtom('Distance', start, end)].property_()
        return -1

    def update_distance(self, start: ('int', 'int'), end: ('int', 'int')) -> 'int':
        '''If shortest path is ocluded by an object, then change the distance'''
        pass

    def shortest_path(self, start: ('int', 'int'), end: ('int', 'int')) -> []:
        pass

    def check_if_connected(self, start: ('int', 'int'), end: ('int', 'int')) -> 'bool':
        return StaticAtom('Distance', start, end) in self.rigid_atoms

    def find_box(self, position):  #### WHAT DOES IT DO ??
        for atom in self.atoms:
            if atom.name == "BoxAt" and atom.variables[1] == position:
                return atom
        return False

    def find_box_position(self, name: 'str'):
        atom = StaticAtom('BoxAt^', name)
        if atom in self.atoms:
            return self.atoms[atom].property()
        return False

    def find_box_color(self, box: 'str') -> ('str'):
        atom = StaticAtom('Color*', box)
        if atom in self.rigid_atoms:
            return self.rigid_atoms[atom].property_()
        return False

    def find_box_goal_distance(self, box_name: 'str', goal_name: 'str') -> 'int':
        box_atom = StaticAtom('BoxAt^', box_name)
        if box_atom in self.atoms:
            box_pos = self.atoms[box_atom].property()
        else:
            return -1

        goal_atom = StaticAtom('GoalAt*', goal_name)
        if goal_atom in self.rigid_atoms:
            goal_pos = self.rigid_atoms[goal_atom].property()
        else:
            return -1

        distance = self.find_distance(box_pos, goal_pos)
        return distance

    def find_box_letter(self, box_name: 'str'):  ##### WHAT DOES IT DO?
        atom = StaticAtom('Letter*', box_name)
        if atom in self.rigid_atoms:
            return self.rigid_atoms[atom].property_()

    def find_letter(self, name: 'str'):
        atom = StaticAtom('Letter*', name)
        if atom in self.rigid_atoms:
            return self.rigid_atoms[atom].property_()

    def find_agent(self, name: 'str'):
        atom = StaticAtom('AgentAt^', name)
        if atom in self.atoms:
            return self.atoms[atom].property()
        return False

    def return_agents(self):  # returns name - color - position
        number = 0
        search = True
        agents = []
        while search:
            name = str(number)
            atom = StaticAtom('AgentAt^', name)
            if atom in self.atoms:
                color = self.rigid_atoms[StaticAtom('Color*', name)].property_()
                agents.append((name, color, self.atoms[atom].property()))
                number += 1
            else:
                search = False
        return agents

    def return_matching_boxes(self, goal_name):
        '''Returns a list of boxes that can be placed on the goal'''
        goal_letter = self.find_letter(goal_name)
        #print(goal_name, goal_letter, file=sys.stderr )
        boxes = list()

        number = 1
        search = True
        while search:
            name = 'B' + str(number)
            if StaticAtom('BoxAt^', name) in self.atoms:
                if self.find_letter(name) == goal_letter:
                    boxes.append(name)
                number += 1
            else:
                search = False
        #print(boxes, file=sys.stderr)
        return boxes

    def find_agent_by_position(self, position):  #### WHAT DOES IT DO ??
        for atom in self.atoms:
            if atom.name == "AgentAt" and atom.variables[1] == position:
                return atom
        return False

    def find_object_at_position(self, position: ('int', 'int')):
        for atom in self.atoms:
            if atom.name == "AgentAt" and atom.variables[1] == position:
                return atom
            elif atom.name == "BoxAt" and atom.variables[1] == position:
                return atom
        return False

    def return_goals(self):  # return list of Goal Name - goal position
        number = 1
        search = True
        goals = []
        while search:
            name = 'G' + str(number)
            atom = StaticAtom('GoalAt*', name)
            if atom in self.rigid_atoms:
                goals.append((name, self.find_letter(name), self.rigid_atoms[atom].property_()))
                number += 1
            else:
                search = False
        return goals

    def progression(self):  # returns list of met and unmet goals
        met = []
        unmet = []
        goals = self.return_goals()

        for name, letter, pos in goals:
            box = self.find_box(pos)
            if not box:
                unmet.append((name, letter, pos))
            else:
                if self.find_letter(box.variables[0]) != letter:
                    unmet.append((name, letter, pos))
                else:
                    met.append((name, letter, pos))
        return [unmet, met]

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

        atom = StaticAtom('GoalAt*')
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

    def create_child(self, action, cost=0, h_cost=0, ghostmode=False):
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
        action[0].execute(state, action[1], ghostmode)
        return state

    def all_atoms(self) -> 'KnowledgeBase':
        return self.atoms + self.rigid_atoms

    def reset_state(self):
        self.last_action = {'action': 'NoOp', 'params': [], 'message': ['NoOp'], 'priority': 0.7}
        self.cost = 0
        self.h_cost = 0
        self.parent = None

    def f(self) -> 'float':
        return self.__total_cost__()

    ############################
    ##Private or implicit methods

    def __total_cost__(self) -> 'float':
        return self.cost + self.h_cost + self.last_action['priority']

    def __eq__(self, other: 'State'):
        return self.atoms == other.atoms #and self.last_action['priority'] == other.last_action['priority']

    def __str__(self):
        state_str = "State " + self.name + "\n"
        state_str += str(self.rigid_atoms)
        state_str += str(self.atoms)

        return (state_str)

    def __hash__(self) -> 'int':
        hash_value = 0
        for atom in self.atoms:
            hash_value += hash(atom)
        return hash_value

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
