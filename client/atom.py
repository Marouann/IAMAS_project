# In our main Domain the atoms of the State are the following:
# The cells : Atom('L', [x, y]) (x, y the coordinates)
# The goals : Atom('Goal', [i]) (the goals are enumerated)
# The boxed : Atom('Box', [i]) (the boxes are enumerated)
# The colors : Atom('IsColor', [c])
# The letter of boxes : Atom('Letter', [i, A]) (i is the box, and 'A' a caps letter)
# The letter of goals : Atom('Letter', [i, a]) (i is the goal, and 'a' a small letter)
# The color of objects : Atom('Color', [obj, c])
# The position of boxes: Atom('BoxAt', [i, x, y])
# The position of goals: Atom('GoalAt', [i, x, y])
# The free cells : Atom('Free', [x ,y])

class Atom:
    def __init__(self, name, variables):
        self.name = name
        self.variables = variables
        self.arity = len(variables)
    
    # replace_variables
    # variables_map is a dict, example { variableToReplace: value }
    # replace_variables is used to convert precondition Atom of actions
    # For example replace_variables(Atom('On', ['A', 'x']), { x: 2 }) = Atom('On', ['A', '2']);
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
            var_string += str(var)
            var_string += ", "
        var_string = var_string[:-2]
        return "Atom: " + self.name +"(" + var_string + ")"
