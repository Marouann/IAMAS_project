from action import Action
from atom import Atom

p1 = Atom("On",["A", (1,2)])
p2 = Atom("On",["A", (1,2)])
b1 = Atom("Box", [(1,2)])
b2 = Atom("Box", [(1,2)])

s0 = State("s0", [p1, p2, b1, b2])
print(s0)

move = Action(name= "Move",
              preconditions=lambda x: [Atom("Box", [x]),
                              Atom("On", ["A",x])],
              positive_effects = lambda x: [Atom("On", ["B",x])],
              negative_effects = lambda x: [Atom("On", ["A",x])])

move.checkPreconditions(s0, ["3"])

move.execute(s0, ["2"])
print(s0)
