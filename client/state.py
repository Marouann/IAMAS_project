import sys
from knowledgeBase import KnowledgeBase
from atom import *


class State:
    def __init__(self, name: 'str',
                 goals: '[dict]',
                 atoms: 'KnowledgeBase',
                 rigid_atoms: 'KnowledgeBase',
                 cost=0,
                 h_cost = 0,
                 parent=None,
                 last_action="[NoOp]"):
        self.name = name
        self.goals = goals
        self.atoms = atoms
        self.rigid_atoms = rigid_atoms
        self.parent = parent
        self.last_action = last_action

        self.cost = cost
        self.h_cost = h_cost # cost based on heuristics

    def removeAtom(self, atom: 'Atom'):
        # if atom not in s then do nothing
        try:
            self.atoms.delete(atom)
        except ValueError:
            pass

    def addAtom(self, atom: 'Atom'):
        self.atoms.update(atom)

    # def __len__(self):
    #     return self.atoms.kb.length

    def __eq__(self, other: 'State'):
        return self.atoms == other.atoms  # and self.parent == other.parent and self.last_action == other.last_action

    def __str__(self):
        state_str = "State " + self.name + "\n"

        state_str += str(self.rigid_atoms)

        state_str += str(self.atoms)

        return (state_str)

    def findBox(self, position):
        for atom in self.atoms:
            if atom.name == "BoxAt" and atom.variables[1] == position:
                return atom
        return False

    def findBoxLetter(self, boxName):
        for atom in self.rigid_atoms:
            if atom.name == "Letter" and atom.variables[0] == boxName:
                return atom

    def findAgent(self, agt):
        for atom in self.atoms:
            if atom.name == "AgentAt" and atom.variables[0] == agt:
                return atom.variables[1]

    def getUnmetGoals(self):
        metGoals = []
        unmetGoals = []
        for goal in self.goals:
            box = self.findBox(goal['position'])
            if False == box:
                unmetGoals.append(goal)
            else:
                boxLetter = self.findBoxLetter(box.variables[0])
                letter = boxLetter.variables[1]
                if letter != goal['letter']:
                    unmetGoals.append(goal)
                else:
                    metGoals.append(goal)
        return [unmetGoals, metGoals]

    def copy(self):
        atoms_copy = KnowledgeBase("Atoms")
        atoms_copy.copy(self.atoms)
        return State(name=self.name,
                     goals=self.goals,
                     atoms=atoms_copy,
                     rigid_atoms=self.rigid_atoms,
                     parent=self.parent,
                     cost=self.cost)

    def create_child(self, action, cost=0, h_cost= 0):
        atoms_copy = KnowledgeBase("Atoms")
        atoms_copy.copy(self.atoms)

        state = State(name=self.name,
                      goals=self.goals,
                      atoms=atoms_copy,
                      rigid_atoms=self.rigid_atoms,
                      parent=self,
                      last_action={'action': action[0], 'params': action[1], 'message': action[2]},
                      cost=self.cost + cost,
                      h_cost = h_cost)
        action[0].execute(state, action[1])
        return state

    def total_cost(self) -> 'int':
        return self.cost + self.h_cost

    def atoms(self):
        return self.atoms + self.rigid_atoms

    def __hash__(self):
        return hash(self.atoms)

    def __cmp__(self, other: 'State'):
        if self.total_cost() > other.total_cost():
            return 1
        elif self.total_cost() == other.total_cost():
            return 0
        elif self.total_cost() < other.total_cost():
            return -1

    def __lt__(self, other: 'State'):
        return self.total_cost() < other.total_cost()

    def __gt__(self, other: 'State'):
        return self.total_cost() > other.total_cost()
