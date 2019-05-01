from atom import Atom
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

    def checkPreconditions(self, s: 'State', variables):  ## should it be with a *
        practical = True  ## what does it stands for ?
        i = 0
        preconditions = self.preconditions(*variables)
        while practical and i < len(preconditions):
            actual_atom = preconditions[i]
            practical = practical and (actual_atom in s.atoms or actual_atom in s.rigid_atoms)
            i += 1
        return practical

    def execute(self, s: 'State', variables):
        if self.checkPreconditions(s, variables):

            for effect in self.negative_effects(*variables):
                s.remove_atom(effect)

            for effect in self.positive_effects(*variables):
                s.add_atom(effect)
        else:
            print("This action is not applicable here.", file=sys.stderr, flush=True)
            print(variables, file=sys.stderr)


Move = Action(
    'Move',
    lambda agt, agtFrom, agtTo: [Atom('AgentAt', agt, agtFrom), Atom('Free', agtTo), Atom('Neighbour', agtFrom, agtTo)],
    lambda agt, agtFrom, agtTo: [Atom('AgentAt', agt, agtTo), Atom('Free', agtFrom)],
    lambda agt, agtFrom, agtTo: [Atom('AgentAt', agt, agtFrom), Atom('Free', agtTo)],
)

Push = Action(
    'Push',
    lambda agt, agtFrom, box, boxFrom, boxTo, color: [Atom('AgentAt', agt, agtFrom),
                                                      Atom('Neighbour', agtFrom, boxFrom),
                                                      Atom('BoxAt', box, boxFrom), Atom('Neighbour', boxFrom, boxTo),
                                                      Atom('Free', boxTo),
                                                      Atom('IsColor', color), Atom('Color', agt, color),
                                                      Atom('Color', box, color)],
    lambda agt, agtFrom, box, boxFrom, boxTo, color: [Atom('AgentAt', agt, boxFrom), Atom('Free', agtFrom),
                                                      Atom('BoxAt', box, boxTo)],
    lambda agt, agtFrom, box, boxFrom, boxTo, color: [Atom('AgentAt', agt, agtFrom), Atom('Free', boxTo),
                                                      Atom('BoxAt', box, boxFrom)],
)

Pull = Action(
    'Pull',
    lambda agt, agtFrom, agtTo, box, boxFrom, color: [Atom('AgentAt', agt, agtFrom), Atom('Neighbour', agtFrom, agtTo),
                                                      Atom('BoxAt', box, boxFrom), Atom('Neighbour', boxFrom, agtFrom),
                                                      Atom('Free', agtTo),
                                                      Atom('IsColor', color), Atom('Color', agt, color),
                                                      Atom('Color', box, color)],
    lambda agt, agtFrom, agtTo, box, boxFrom, color: [Atom('AgentAt', agt, agtTo), Atom('Free', boxFrom),
                                                      Atom('BoxAt', box, agtFrom)],
    lambda agt, agtFrom, agtTo, box, boxFrom, color: [Atom('AgentAt', agt, agtFrom), Atom('Free', agtTo),
                                                      Atom('BoxAt', box, boxFrom)],
)

NoOp = Action(
    'NoOp',
    lambda agt, agtFrom: [Atom('AgentAt', agt, agtFrom)],
    lambda agt, agtFrom: [Atom('AgentAt', agt, agtFrom)],
    lambda agt, agtFrom: [Atom('AgentAt', agt, agtFrom), Atom('Free', agtFrom)],
)
