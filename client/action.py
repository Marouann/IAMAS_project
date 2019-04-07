from atom import Atom
import sys

class Action:
    '''
        variables can be anything when defining the actions, they will be replaced by actual variables
        at applicability check or at execution of the action
    '''

    def __init__(self, name, preconditions, positive_effects, negative_effects):
        self.name = name # Move, Push, Pull.
        self.preconditions = preconditions
        self.positive_effects = positive_effects
        self.negative_effects = negative_effects


    def checkPreconditions(self, s, variables):
        practical = True
        i = 0
        preconditions = self.preconditions(*variables)
        while practical and i<len(preconditions):
            actual_atom = preconditions[i]
            practical = practical and (actual_atom in s.atoms or actual_atom in s.rigid_atoms)
            i += 1
        return practical

    def execute(self, s, variables):
        if self.checkPreconditions(s, variables):

            for effect in self.negative_effects(*variables):
                s.removeAtom(effect)

            for effect in self.positive_effects(*variables):
                s.addAtom(effect)
        else:
            print("This action is not applicable here.")


Move = Action(
    'Move',
    lambda agt, agtFrom, agtTo: [Atom('AgentAt', agt, agtFrom), Atom('Free', agtTo), Atom('Neighbour', agtFrom, agtTo)],
    lambda agt, agtFrom, agtTo: [Atom('AgentAt', agt, agtTo), Atom('Free', agtFrom)],
    lambda agt, agtFrom, agtTo: [Atom('AgentAt', agt, agtFrom), Atom('Free', agtTo)],
)

Push = Action(
    'Push',
    lambda agt, agtFrom, box, boxFrom, boxTo, color: [Atom('AgentAt', agt, agtFrom), Atom('Neighbour', agtFrom, boxFrom),
        Atom('BoxAt', box, boxFrom), Atom('Neighbour', boxFrom, boxTo), Atom('Free', boxTo),
        Atom('IsColor', color), Atom('Color', agt, color), Atom('Color', box, color)],
    lambda agt, agtFrom, box, boxFrom, boxTo, color: [Atom('AgentAt', agt, boxFrom), Atom('Free', agtFrom),  Atom('BoxAt', box, boxTo)],
    lambda agt, agtFrom, box, boxFrom, boxTo, color: [Atom('AgentAt', agt, agtFrom), Atom('Free', boxTo),  Atom('BoxAt', box, boxFrom)],
)

Pull = Action(
    'Pull',
    lambda agt, agtFrom, agtTo, box, boxFrom, color: [Atom('AgentAt', agt, agtFrom), Atom('Neighbour', agtFrom, agtTo),
        Atom('BoxAt', box, boxFrom), Atom('Neighbour', boxFrom, agtFrom), Atom('Free', agtTo),
        Atom('IsColor', color), Atom('Color', agt, color), Atom('Color', box, color)],
    lambda agt, agtFrom, agtTo, box, boxFrom, color: [Atom('AgentAt', agt, agtTo), Atom('Free', boxFrom),  Atom('BoxAt', box, agtFrom)],
    lambda agt, agtFrom, agtTo, box, boxFrom, color: [Atom('AgentAt', agt, agtFrom), Atom('Free', agtTo),  Atom('BoxAt', box, boxFrom)],
)
