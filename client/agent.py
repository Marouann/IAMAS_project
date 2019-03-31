import sys

class Agent:
    def __init__(self, agt, position, goal, actions, color):
        self.agt = agt
        self.position = position
        self.goal = goal
        self.actions = actions
        self.color = color

    def getPossibleActions(self, s):
        possibleActions = []
        N = (-1,  0, 'N')
        S = ( 1,  0, 'S')
        E = ( 0,  1, 'E')
        W = ( 0, -1, 'W')

        for action in self.actions:
            for dir in [N,S,E,W]:
                agtTo = (self.position[0]+dir[0], self.position[1]+dir[1])
                if action.name == "Move":
                    if action.checkPreconditions(s, [self.agt, self.position, agtTo]):
                        possibleActions.append((action, [self.agt, self.position, agtTo], "Move(" + dir[2] + ")", agtTo))
                elif action.name == "Push":
                    for second_dir in [N,S,E,W]:
                        boxFrom = agtTo #the agent will take the place of box
                        boxTo = (boxFrom[0]+second_dir[0], boxFrom[1]+second_dir[1])
                        box = s.findBox(boxFrom)
                        if box:
                            boxName = box.variables[0]
                            if action.checkPreconditions(s, [self.agt, self.position, boxName, boxFrom, boxTo, self.color]): # we also need box somehow
                                possibleActions.append((action,
                                                        [self.agt, self.position, boxName, boxFrom, boxTo, self.color],
                                                        "Push(" + dir[2] + "," + second_dir[2] + ")",
                                                        agtTo))
                elif action.name == "Pull":
                    for second_dir in [N,S,E,W]:
                        boxFrom = (self.position[0]+second_dir[0], self.position[1]+second_dir[1])
                        box = s.findBox(boxFrom)
                        if box:
                            boxName = box.variables[0]
                            color = s.findBoxColor(boxName)
                            if action.checkPreconditions(s, [self.agt, self.position, agtTo, boxName, boxFrom, color]): # we also need box somehow
                                possibleActions.append((action,
                                                        [self.agt, self.position, agtTo, boxName, boxFrom, color],
                                                        "Pull(" + dir[2] + "," + second_dir[2] + ")",
                                                        agtTo))
        return possibleActions
