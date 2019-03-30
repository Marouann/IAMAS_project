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

    def update(self, atom, feedback=False):
        if not self.__isin__(atom):
            self.kb[atom] = atom
            if feedback: print('[KB] Added', atom)
        else:
            if feedback: print('[KB] Cannot update', atom)

    def update_nonAtom(self, name, *variables, feedback=False):
        atom = Atom(name, *variables)
        self.update(atom, feedback)

    def delete(self, atom, feedback=False):
        if self.__isin__(atom):
            del self.kb[atom]
            if feedback: print('[KB] Deleted', atom)
        else:
            if feedback: print('[KB] Cannot delete', atom)

    def clear(self, feedback=False):
        self.kb.clear()
        if feedback: print('[KB] Cleared')

    def len(self, feedback=False):
        if feedback: print('[KB] Length:', self.kb.__len__())
        return self.kb.__len__()

    def is_empty(self):
        return self.len() == 0


