from typing import Dict, Any

from atom import Atom
import sys

# Knowledge Base contain the literals for the state
# kb is a dictionary
# kb[key] = value , key is a hashed version of atom and value is the atom itself

class KnowledgeBase():
    def __init__(self, name=''):
        self.__kb = {}
        self.name = name
    def __isin__(self, atom):
        return atom in self.__kb

    def update(self, atom, feedback=False):
        if not isinstance(atom, Atom): pass
        if not self.__isin__(atom):
            self.__kb[atom] = atom
            if feedback: print('[KB] Added', atom, flush=True)
        else:
            if feedback: print('[KB] Cannot update', atom, flush=True)

    def delete(self, atom, feedback=False):
        if not isinstance(atom,Atom): pass
        if self.__isin__(atom):
            del self.__kb[atom]
            if feedback: print('[KB] Deleted', atom, flush=True)
        else:
            if feedback: print('[KB] Cannot delete', atom, flush=True)

    def clear(self, feedback=False):
        self.__kb.clear()
        if feedback: print('[KB] Cleared', flush=True)

    def len(self, feedback=False):
        if feedback: print('[KB] Length:', self.__kb.__len__(), flush=True)
        return self.__kb.__len__()

    def is_empty(self):
        return self.len() == 0

    def kb(self):
        return self.__kb.copy()

    def copy(self, KnowledgeBase):
        self.__kb = KnowledgeBase.kb()

    def __str__(self):
        values = '\n' + self.name + ' CONTAINS: \n'
        if not self.is_empty():
            for v in self.__kb.keys():
                values += '  ' + str(v) + '\n'
        return values

    def __eq__(self, other):
        if not isinstance(other, KnowledgeBase): return False
        return self.__kb == other.kb()

    def __getitem__(self, key):
        return self.__kb[key]

    def __iter__(self):
        return self.__kb.__iter__()

    def items(self):
        return self.__kb.items()

