class Action:
    '''
        variables can be anything when defining the actions, they will be replaced by actual variables
        at applicability check or at execution of the action
    '''
    
    def __init__(self, name, preconditions, positive_effects, negative_effects, variables):
        # Name of the action, string
        self.name = name
        # Preconditions, list of Atom
        self.preconditions = preconditions
        # Positive effects, list of Atom
        self.positive_effects = positive_effects
        # Negative effects, list of Atom
        self.negative_effects = negative_effects
        # List of the variables, list of string
        self.variables = variables
    
    # checkPreconditions, return True if the preconditions are met
    def checkPreconditions(self, state, variables):
        practical = True
        i = 0
        variable_map = self.createVariableMap(variables)
        while practical and i<len(self.preconditions):
            actual_atom = self.preconditions[i].replace_variables(variable_map)
            practical = practical and (actual_atom in state.atoms)
            i += 1 
        return practical
    
    # execute, modify the state if the preconditions are met
    def execute(self, state, variables):
        if self.checkPreconditions(state, variables):
            variable_map = self.createVariableMap(variables)

            for effect in self.negative_effects:
                state.removeAtom(effect.replace_variables(variable_map))

            for effect in self.positive_effects:
                state.addAtom(effect.replace_variables(variable_map))
        else:
            print("This action is not applicable here.")
            
    # createVariableMap, return a dict of the variables that have to be replaced
    def createVariableMap(self, variables):
        variable_map = {}
        if len(variables) != len(self.variables):
            print("Wrong number of variables given. Please check action schema.")
            return None
       
        for i, var in enumerate(self.variables):
            variable_map[var] = variables[i]
            
        return variable_map
        