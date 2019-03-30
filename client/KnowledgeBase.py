from atom import Atom
# Knowledge Base contain the literals for the state
# kb is a dictionary
# kb[key] = value , key is a hashed version of atom and value is the atom itself

class KnowledgeBase():
    def __init__(self):
        self.kb = {}

    def __call__(self, atom):
        return self.kb[atom]

    def __isin__(self, atom):
        return atom in self.kb

    def update(self, atom):
        if not self.__isin__(atom):
            self.kb[atom] = atom
            print('KB: added', atom)
        else:
            print('KB: cannot add', atom)

    def update_nonAtom(self, name, *variables):
        atom = Atom(name, *variables)
        self.update(atom)

    def delete(self, atom):
        if self.__isin__(atom):
            del self.kb[atom]
            print('KB deleted:', atom)
        else:
            print('KB cannot delete:', atom)

    def clear(self):
        self.kb.clear()

    def len(self):
        return self.kb.__len__()

    def is_empty(self):
        return self.len() == 0


