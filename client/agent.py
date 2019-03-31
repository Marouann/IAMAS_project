class Agent:
    def __init__(self, agt, position, goal):
        self.agt = agt
        self.position = position
        self.goal = goal
        self.actions = actions

    def getPossibleActions(self, s):
        possibleActions = []
        N = (-1,  0)
        S = ( 1,  0)
        E = ( 0,  1)
        W = ( 0, -1)
        for action in self.actions:
            for dir in [N,S,E,W]:
                agtTo = (position[0]+dir[0], position[1]+dir[1])
                if action.name == "Move":
                    if action.checkPreconditions(s, [position, agtTo]):
                        possibleActions.append((action, [position, agtTo], "Move(" + str(dir) + ")" ))
                elif action.name == "Push":
                    for second_dir in [N,S,E,W]:
                        boxFrom = agtTo #the agent will take the place of box
                        boxTo = (boxFrom[0]+second_dir[0], boxFrom[1]+second_dir[1])
                        box = s.findBox(boxFrom).variables[0]
                        color = s.findBoxColor(box)
                        if action.checkPreconditions(s, [self.agt, position, boxName, boxFrom, boxTo, color]): # we also need box somehow
                            possibleActions.append((action, [self.agt, position, boxName, boxFrom, boxTo, color], "Push(" + str(dir) + "," + second_dir + ")"))
                elif action.name == "Pull":
                    for second_dir in [N,S,E,W]:
                        boxFrom = (position[0]+second_dir[0], position[1]+second_dir[1])
                        box = s.findBox(boxFrom).variables[0]
                        color = s.findBoxColor(box)
                        if action.checkPreconditions(s, [self.agt, position, box, boxFrom, boxTo, color]): # we also need box somehow
                            possibleActions.append((action, [self.agt, position, box, boxFrom, boxTo, color], "Pull(" + str(dir) + "," + second_dir + ")"))
        return possibleActions
