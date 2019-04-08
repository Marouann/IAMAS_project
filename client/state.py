import sys
from knowledgeBase import KnowledgeBase
from atom import *

class State:
    def __init__(self, name: 'str',
                 atoms:'KnowledgeBase',
                 rigid_atoms:'KnowledgeBase',
                 cost = 0,
                 parent = None,
                 last_action = "NoOp"):
        self.name = name
        self.atoms = atoms
        self.rigid_atoms = rigid_atoms
        self.parent = parent
        self.last_action = last_action

        self.cost = cost #current cost of the state  TO DISCUSS

        self.agent_hash = {}
        self.box_hash = {}

    def removeAtom(self, atom: 'Atom'):
        # if atom not in s then do nothing
        try:
            self.atoms.delete(atom)
        except ValueError:
            pass

    def addAtom(self, atom:'Atom'):
        self.atoms.update(atom)

    # def __len__(self):
    #     return self.atoms.kb.length

    def __eq__(self, other:'State'):
        return self.atoms == other.atoms #and self.parent == other.parent and self.last_action == other.last_action

    def __str__(self):
        state_str = "State " + self.name + "\n"

        state_str += str(self.rigid_atoms)

        state_str += str(self.atoms)

        return(state_str)

    def findBox(self,position):
        for atom in self.atoms:
            if atom.name == "BoxAt" and atom.variables[1] == position:
                return atom

    def findAgent(self, agt):
        for atom in self.atoms:
            if atom.name == "AgentAt" and atom.variables[0] == agt:
                return atom.variables[1]

    def copy(self):
        atoms_copy = KnowledgeBase("Atoms")
        atoms_copy.copy(self.atoms)
        return State(name=self.name,
                     atoms=atoms_copy,
                     rigid_atoms=self.rigid_atoms,
                     parent=self.parent,
                     cost=self.cost+1)

    ##RETURN ALL ATOMS
    def atoms(self):
        return self.atoms + self.rigid_atoms
