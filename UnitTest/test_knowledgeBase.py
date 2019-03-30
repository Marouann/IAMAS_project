from unittest import TestCase
from KnowledgeBase import KnowledgeBase
from atom import Atom


class TestKnowledgeBase(TestCase):
    def test_update(self):
        kb = KnowledgeBase()
        kb.update(Atom('At', 'A1', 'C12'))
        kb.update(Atom('At', 'A1', 'C12'))
        self.assert_(kb.len()==1)

    def test_delete(self):
        kb = KnowledgeBase()
        kb.update(Atom('At', 'A1', 'C12'))
        kb.delete(Atom('At', 'A1', 'C12'))
        self.assert_(kb.len()==0)

    def test_clear(self):
        kb = KnowledgeBase()
        kb.update(Atom('At', 'A1', 'C12'))
        kb.update(Atom('At', 'A2', 'C32'))
        kb.clear()
        self.assert_(kb.len()==0)

    def test_len(self):
        kb = KnowledgeBase()
        kb.update(Atom('At', 'A1', 'C12'))
        kb.update(Atom('At', 'A1', 'C12'))
        kb.update(Atom('At', 'A2', 'C32'))
        kb.delete(Atom('At', 'A1', 'C12'))
        self.assert_(kb.len()==1)

    def test_is_empty(self):
        kb = KnowledgeBase()
        kb.update(Atom('At', 'A1', 'C12'))
        kb.update(Atom('At', 'A2', 'C32'))
        kb.update(Atom('At', 'A3', 'C32'))
        self.assert_(kb.len()==3)
