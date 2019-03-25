from newState import State
from action import Action
from atom import Atom

p1 = Atom("On",["A", "1"])
p2 = Atom("On",["A", "2"])
b1 = Atom("Box", ["1"])
b2 = Atom("Box", ["2"])

s0 = State("s0", [p1, p2, b1, b2])
print(s0)

move = Action(name= "Move", 
                preconditions= [Atom("Box", ['x']), 
                                Atom("On", ["A","x"])],
                positive_effects = [Atom("On", ["B","x"])],
                negative_effects = [Atom("On", ["A","x"])], 
                variables = ["x"])

move.checkPreconditions(s0, ["3"])

move.execute(s0, ["2"])
print(s0)
