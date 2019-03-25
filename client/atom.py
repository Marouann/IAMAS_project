class Atom:
    def __init__(self, name, variables):
        self.name = name
        self.variables = variables
        self.arity = len(variables)
    
    # replace_variables
    # variables_map is a dict, example { variableToReplace: value }
    # replace_variables is used to convert precondition Atom of actions
    # For example replace_variables(Atom('On', [A', 'x']), { x: 2 }) = Atom('On', ['A', '2']);
    def replace_variables(self, variable_map):
        var_to_replace = []
        try:
            var_to_replace = list(filter(lambda var: var in variable_map, self.variables))
            actual_atom = Atom(self.name, [variable_map[var] if var in var_to_replace else var for var in self.variables])
            return actual_atom
        except KeyError:
            print("Wrong variables given to action.")
        
    def __eq__(self, other):
        return self.name == other.name and self.arity == other.arity and self.variables == other.variables
    
    def __str__(self):
        var_string = ""
        for var in self.variables:
            var_string += var
            var_string += ", "
        var_string = var_string[:-2]
        return "Atom: " + self.name +"(" + var_string + ")"
