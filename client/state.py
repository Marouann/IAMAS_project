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
                 last_action=  {'action': 'NoOp', 'params': [], 'message': []}
                 ):
        self.name = name
        self.goals = goals
        self.atoms = atoms
        self.rigid_atoms = rigid_atoms
        self.parent = parent
        self.last_action = last_action

        self.cost = cost
        self.h_cost = h_cost  # cost based on heuristics

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

    def findBoxGoalDistance(self, name, goalAtom):
        boxAtom = Atom
        for atom in self.atoms:
            if atom.name == "BoxAt" and atom.variables[0] == name:
                boxAtom = atom
                break
        distance = self.getDistance(boxAtom.variables[1], goalAtom["position"])
        return distance

    def getDistance(self, firstLocation, secondLocation):
        distance = math.sqrt(math.pow(secondLocation[0] - firstLocation[0], 2) +
                             math.pow(secondLocation[1] - firstLocation[1], 2))
        return distance

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
        state.last_action = {'action': action[0], 'params': action[1], 'message': action[2]}
        #print(action,file=sys.stderr, flush=True)
        action[0].execute(state, action[1])
        return state

    def __total_cost__(self) -> 'int':
        return self.cost + self.h_cost

    def atoms(self):
        return self.atoms + self.rigid_atoms

    def __hash__(self):
        #print(self.last_action)
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
