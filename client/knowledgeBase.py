from atom import Atom
import sys

# Knowledge Base contain the literals for the state
# kb is a dictionary
# kb[key] = value , key is a hashed version of atom and value is the atom itself

class KnowledgeBase():
    def __init__(self):
        self.kb = {}

    def __isin__(self, atom):
        return atom in self.kb

    def update(self, atom, feedback=False):
        if not isinstance(atom, Atom): pass
        if not self.__isin__(atom):
            self.kb[atom] = atom
            if feedback: print('[KB] Added', atom, flush=True)
        else:
            if feedback: print('[KB] Cannot update', atom, flush=True)

    def update_nonAtom(self, name, *variables, feedback=False):
        atom = Atom(name, *variables)
        self.update(atom, feedback)

    def delete(self, atom, feedback=False):
        if not isinstance(atom,Atom): pass
        if self.__isin__(atom):
            del self.kb[atom]
            if feedback: print('[KB] Deleted', atom, flush=True)
        else:
            if feedback: print('[KB] Cannot delete', atom, flush=True)

    def clear(self, feedback=False):
        self.kb.clear()
        if feedback: print('[KB] Cleared', flush=True)

    def len(self, feedback=False):
        if feedback: print('[KB] Length:', self.kb.__len__(), flush=True)
        return self.kb.__len__()

    def is_empty(self):
        return self.len() == 0

    def content(self):
        return self.kb.copy()

    def __str__(self):
        values = '\n[KB] CONTAINS: \n'
        if not self.is_empty():
            for v in self.kb.keys():
                values += '  ' + str(v) + '\n'
        return values

    def __eq__(self, other):
        if not isinstance(other, KnowledgeBase): return False
        return self.kb == other.kb
