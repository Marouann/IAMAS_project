import sys

class State:
    def __init__(self, name, atoms, rigid_atoms, parent = None, last_action = "NoOp"):
        self.name = name
        self.atoms = atoms
        self.rigid_atoms = rigids_atoms
        self.parent = parent
        self.last_action = last_action

    def removeAtom(self, atom):
        # if atom not in s then do nothing
        try:
            self.atoms.delete(atom)
        except ValueError:
            pass

    def addAtom(self, atom):
        self.atoms.update(atom)

    def __len__(self):
        return self.length

    def __eq__(self, other):
        return self.atoms == other.atoms #and self.parent == other.parent and self.last_action == other.last_action

    def __str__(self):
        state_str = "State " + self.name + "\n \nRigid Atoms: \n"

        for atom in self.rigid_atoms:
            state_str += str(atom)[6:] + "^"

        state_str =  state_str[:-1]
        state_str += "\n \nAtoms: \n"

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
        return State(self.name, self.atoms.copy(), self.rigid_atoms, self.parent)
