class State:
    def __init__(self, name, atoms):
        # name, string
        self.name = name
        # atoms, list of Atom
        self.atoms = atoms
        # length, int
        self.length = len(atoms)
    
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
        return self.atoms == other.atoms
    
    def __str__(self):
        state_str = "State " + self.name + ": "
        for atom in self.atoms:
            state_str += str(atom)[6:] + "^"
        return state_str[:-1]
    
    def copy(self):
        return State(s.name, s.atoms.copy())
    