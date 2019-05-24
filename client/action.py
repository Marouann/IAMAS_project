from atom import Atom, DynamicAtom
from state import State
import sys


class Action:
    '''
        variables can be anything when defining the actions, they will be replaced by actual variables
        at applicability check or at execution of the action
    '''

    def __init__(self, name: 'str', preconditions, positive_effects, negative_effects):
        self.name = name  # Move, Push, Pull.
        self.preconditions = preconditions  # type?
        self.positive_effects = positive_effects  # type?
        self.negative_effects = negative_effects  # type?

    def checkPreconditions(self, s: 'State', variables, ghostmode=False):  ## should it be with a *
        practical = True  ## what does it stands for ?
        i = 0
        preconditions = self.preconditions(*variables)
        while practical and i < len(preconditions):
            actual_atom = preconditions[i]

            # # print(actual_atom, file=sys.stderr)
            # # print(s.atoms, file=sys.stderr)
            if not ghostmode or actual_atom.name != "Free":
                practical = practical and (actual_atom in s.atoms or actual_atom in s.rigid_atoms)
            i += 1
        return practical

    def execute(self, s: 'State', variables, ghostmode=False):
        if self.checkPreconditions(s, variables, ghostmode=ghostmode):

            for effect in self.negative_effects(*variables):
                s.remove_atom(effect)

            for effect in self.positive_effects(*variables):
                s.add_atom(effect)

Move = Action(
    'Move',
    lambda agt, agtFrom, agtTo: [Atom('AgentAt', agt, agtFrom), DynamicAtom('AgentAt^', agtFrom, agt),
                                 Atom('Free', agtTo), Atom('Neighbour', agtFrom, agtTo)],
    lambda agt, agtFrom, agtTo: [Atom('AgentAt', agt, agtTo), DynamicAtom('AgentAt^', agtTo, agt),
                                 Atom('Free', agtFrom)],
    lambda agt, agtFrom, agtTo: [Atom('AgentAt', agt, agtFrom), DynamicAtom('AgentAt^', agtFrom, agt),
                                 Atom('Free', agtTo)],
)

Push = Action(
    'Push',
    lambda agt, agtFrom, box, boxFrom, boxTo, color: [Atom('AgentAt', agt, agtFrom), DynamicAtom('AgentAt^', agtFrom, agt),
                                                      Atom('Neighbour', agtFrom, boxFrom),
                                                      Atom('BoxAt', box, boxFrom), DynamicAtom('BoxAt^', boxFrom, box),
                                                      Atom('Neighbour', boxFrom, boxTo),
                                                      Atom('Free', boxTo),
                                                      Atom('IsColor', color), Atom('Color', agt, color),
                                                      Atom('Color', box, color)],
    lambda agt, agtFrom, box, boxFrom, boxTo, color: [Atom('AgentAt', agt, boxFrom), DynamicAtom('AgentAt^', boxFrom, agt),
                                                      Atom('Free', agtFrom),
                                                      Atom('BoxAt', box, boxTo), DynamicAtom('BoxAt^', boxTo, box)],
    lambda agt, agtFrom, box, boxFrom, boxTo, color: [Atom('AgentAt', agt, agtFrom), DynamicAtom('AgentAt^', agtFrom, agt),
                                                      Atom('Free', boxTo),
                                                      Atom('BoxAt', box, boxFrom), DynamicAtom('BoxAt^', boxFrom, box),
                                                      Atom('Free', boxFrom)],
)

Pull = Action(
    'Pull',
    lambda agt, agtFrom, agtTo, box, boxFrom, color: [Atom('AgentAt', agt, agtFrom), DynamicAtom('AgentAt^', agtFrom, agt),
                                                      Atom('Neighbour', agtFrom, agtTo),
                                                      Atom('BoxAt', box, boxFrom), DynamicAtom('BoxAt^', boxFrom, box),
                                                      Atom('Neighbour', boxFrom, agtFrom),
                                                      Atom('Free', agtTo),
                                                      Atom('IsColor', color), Atom('Color', agt, color),
                                                      Atom('Color', box, color)],
    lambda agt, agtFrom, agtTo, box, boxFrom, color: [Atom('AgentAt', agt, agtTo), DynamicAtom('AgentAt^', agtTo, agt),
                                                      Atom('Free', boxFrom),
                                                      Atom('BoxAt', box, agtFrom), DynamicAtom('BoxAt^', agtFrom, box)],
    lambda agt, agtFrom, agtTo, box, boxFrom, color: [Atom('AgentAt', agt, agtFrom), DynamicAtom('AgentAt^', agtFrom, agt),
                                                      Atom('Free', agtTo),
                                                      Atom('BoxAt', box, boxFrom), DynamicAtom('BoxAt^', boxFrom, box),
                                                      Atom('Free', agtFrom)],
)

NoOp = Action(
    'NoOp',
    lambda agt, agtFrom: [Atom('AgentAt', agt, agtFrom)],
    lambda agt, agtFrom: [Atom('AgentAt', agt, agtFrom)],
    lambda agt, agtFrom: [Atom('Free', agtFrom)],
)
