from atom import *
from KnowledgeBase import *

kb = KnowledgeBase()

atom = Atom('Agent', 'A3')
kb.update(atom)
atom = Atom('At', 'A3', 'C12')
kb.update(atom)

atom = Atom('Color', 'A3', 'red')
kb.update(atom)
atom = Atom('At', 'A3', 'C12')
kb.update(atom)
print(kb(atom))

kb.delete(atom)
kb.delete(atom)
##

print(kb.len())
kb.clear()
print(kb.len())
print(kb.is_empty())




