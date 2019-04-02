from KnowledgeBase import *
from atom import *

kb = KnowledgeBase()
atom = Atom('At', 'A1', 'C56')
kb.update(atom)
kb.update_nonAtom('At', 'A2', 'C48')
atom = Atom('At', 'A2', 'C48')
kb.update(atom, feedback=True)
kb.len(feedback=True)
kb.delete(atom)
kb.len(feedback=True)

kb.update_nonAtom('At1', 'A2', 'C48')
kb.update_nonAtom('At2', 'A2', 'C48')
kb.update_nonAtom('At3', 'A2', 'C48')
kb.update_nonAtom('At4', 'A2', 'C48')

kb1 = KnowledgeBase()
kb1.kb = kb.content()

atom = Atom('A', 'C11')
kb.update(atom)
atom = Atom('A', 'C21')
kb1.update(atom)
print(kb == kb1)
print(kb)