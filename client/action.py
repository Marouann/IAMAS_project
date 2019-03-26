class Action:
    '''
        variables can be anything when defining the actions, they will be replaced by actual variables
        at applicability check or at execution of the action
    '''

    def __init__(self, name, preconditions, positive_effects, negative_effects):
        self.name = name # Use capital letter for action names: MOVE, PUSH, PULL.
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
