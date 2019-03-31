import sys

class State:
    def __init__(self, name, atoms, rigid_atoms, parent = None, last_action = "NoOp"):
        self.name = name
        self.atoms = atoms
        self.rigid_atoms = rigid_atoms
        self.length = len(atoms)
        self.parent = parent
        self.last_action = last_action

    def removeAtom(self, atom):
        # if atom not in s then do nothing
        try:
            self.atoms.remove(atom)
            self.length -= 1
        except ValueError:
            pass

    def addAtom(self, atom):
        self.atoms.append(atom)
        self.length += 1

    def __len__(self):
        return self.length

    def __eq__(self, other):
        return set(self.atoms) == set(other.atoms) #and self.parent == other.parent and self.last_action == other.last_action

    def __str__(self):
        state_str = "State " + self.name + "\n \nRigid Atoms: \n"

        for atom in self.rigid_atoms:
            state_str += str(atom)[6:] + "^"

        state_str =  state_str[:-1]
        state_str += "\n \nAtoms: \n"

        for atom in self.atoms:
            state_str += str(atom)[6:] + "^"
        return state_str[:-1]

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
