from atom import Atom, DynamicAtom


# Knowledge Base contain the literals for the state
# kb is a dictionary
# kb[key] = value , key is a hashed version of atom and value is the atom itself


class KnowledgeBase:
    """" Knowledge Base is an optimized dictionary that allows storage and fast retrieval of Atoms in a State
    __kb is a dictionary
    kb[key] = value : key is a hashed version of atom and value is the atom itself
    """
    def __init__(self, name=None):
        self.__kb = {}
        self.name = name

    def __isin__(self, atom: 'Atom') -> 'bool':
        """"Check if an atom is in the Knowledge base (allows to use in operator)"""
        return atom in self.__kb

    def update(self, atom: 'Atom'):
        """"Add an atom to the Knowledge Base"""
        if not self.__isin__(atom):
            self.__kb[atom] = atom

    def delete(self, atom: 'Atom'):
        """"Delete an atom from the Knowledge Base"""
        if self.__isin__(atom):
            del self.__kb[atom]

    def clear(self):
        """"Delete all contents of the Knowledge Base"""
        self.__kb.clear()

    def len(self) -> 'int':
        """"Number of Atoms in the Knowledge Base"""
        return self.__kb.__len__()

    def is_empty(self) -> 'bool':
        """"Check if Knowledge Base contains any Atoms"""
        return self.len() == 0

    def kb(self) -> 'dict':
        """"Ŗeturn the dictionary with Atoms"""
        return self.__kb

    def return_properties(self, atom:'DynamicAtom'):
        if atom in self.__kb:
            return self.__kb[atom].property()

    def __contains__(self, key) -> 'bool':
        """"Check if the key (hashed version of the object) is contained in the Knowledge Base"""
        return key in self.__kb

    def copy(self, other: 'KnowledgeBase'):
        """"Create a hard copy of the Knowledge Base"""
        self.__kb = other.kb().copy()

    def __str__(self) -> 'str':
        values = '\n' + self.name + ' CONTAINS: \n'
        if not self.is_empty():
            for v in self.__kb.keys():
                values += '  ' + str(v) + '\n'
        return values

    def __eq__(self, other) -> 'bool':
        """"Check if two Knowledge Bases contain same set of Atoms"""
        if not isinstance(other, KnowledgeBase): return False
        return self.__kb == other.kb()

    def __iter__(self):
        """"Specifies how to iterate throught the Knowledge Base's dictionary"""
        return self.__kb.__iter__()

    def __add__(self, other: 'KnowledgeBase') -> 'KnowledgeBase':
        """"Specifies how to add elements of different Knowledge Bases (allows to use + operator)"""
        self.__kb.update(other.__kb)

        return self

    def items(self):
        """"Returns items(values) that are stored in the KB's dictionary"""
        return self.__kb.items()

    def __getitem__(self, item):
        return self.__kb[item]

    def __hash__(self) -> 'int':
        """"Specifies how to hash the dictionary of the Knowledge Base"""
        hash_value = 0
        for item in self.__kb:
            hash_value += hash(item)
        return int(hash_value)
