from client.Action import *

class Agent:
    def __init__(self, position, goal):
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
                if action.name == "MOVE":
                    if action.checkPreconditions(s, [position, agtTo]):
                        possibleActions.append((action, [position, agtTo]))
                elif action.name == "PUSH":
                    for second_dir in [N,S,E,W]:
                        boxFrom = agtTo #the agent will take the place of box
                        boxTo = (boxFrom[0]+second_dir[0], boxFrom[1]+second_dir[1])
                        if action.checkPreconditions(s, [position, boxFrom, boxTo]): # we also need box somehow
                            possibleActions.append((action, [position, boxFrom, boxTo]))
                elif action.name == "PULL":
                    for second_dir in [N,S,E,W]:
                        boxFrom = (position[0]+second_dir[0], position[1]+second_dir[1])
                        if action.checkPreconditions(s, [position, boxFrom, boxTo]): # we also need box somehow
                            possibleActions.append((action, [position, boxFrom, boxTo]))
        return possibleActions
