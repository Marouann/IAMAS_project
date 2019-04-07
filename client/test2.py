from client.knowledgeBase import *
from client.atom import *

kb = KnowledgeBase('test')
p1 = Atom("On",(1,2))
b1 = Atom("Box", [(1,2)])
b2 = Atom("Box", (1,2))
kb.update(p1)
kb.update(b2)
