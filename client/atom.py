# In our main Domain the atoms of the State are the following:
# The colors : Atom('IsColor', [c])
# The letter of boxes : Atom('Letter', [i, A]) (i is the box, and 'A' a caps letter)
# The letter of goals : Atom('Letter', [i, a]) (i is the goal, and 'a' a small letter)
# The color of objects : Atom('Color', [obj, c])
# The position of boxes: Atom('BoxAt', [i, (x, y)])
# The position of goals: Atom('GoalAt', [i, (x, y)])
# The free cells : Atom('Free', [(x, y)])


class Atom:
    """" Data Structure to keep a logical representation of the State"""

    def __init__(self, name: 'str', *variables):
        self.name = name
        self.variables = variables
        self.arity = len(variables)

    def __eq__(self, other):
        """" Comparison of Atoms"""
        if not isinstance(other, Atom): return False
        return self.name == other.name and self.arity == other.arity and self.variables == other.variables

    def __str__(self):
        var_string = ""
        for var in self.variables:
            var_string += str(var)
            var_string += ", "
        var_string = var_string[:-2]
        return "Atom: " + self.name + "(" + var_string + ")"

    def __hash__(self):
        """" Defines the hashing function for the Atom Object"""
        return int(hash(self.name) + hash(self.variables))


class StaticAtom(Atom):
    def __init__(self, name: 'str', *variables):
        self.properties = []
        super().__init__(name, *variables)

    def assign_property(self, *properties):
        self.properties = properties

    def property(self):
        return self.properties

    def property_(self, index=0):
        try:
            return self.property()[0]
        except:
            return self.property()

    def __str__(self):
        var_string = ""
        pro_string = ""
        for var in self.variables:
            var_string += str(var)
            var_string += ", "

        for pro in self.properties:
            pro_string += str(pro)
            pro_string += ", "

        var_string = var_string[:-2]
        pro_string = pro_string[:-2]
        return "Atom*: " + self.name + "(" + var_string + " | " + pro_string + ")"


class DynamicAtom(StaticAtom):
    def __init__(self, name: 'str', properties, *variables):
        super().__init__(name, *variables)
        self.assign_property(properties)

    def assign_property(self, properties):
        self.properties = properties

    def __str__(self):
        var_string = ""
        pro_string = ""
        for var in self.variables:
            var_string += str(var)
            var_string += ", "

        pro_string += str(self.properties)


        var_string = var_string[:-2]
        pro_string = pro_string[:-2]
        return "Atom^: " + self.name + "(" + var_string + " | " + pro_string + ")"