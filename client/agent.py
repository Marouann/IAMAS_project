import sys
from strategy import Strategy
from random import shuffle
from state import State

class Agent:
    def __init__(self, agt, position, goal, actions, color):
        self.agt = agt
        self.position = position
        self.goal = goal
        self.actions = actions
        self.color = color
        self.current_plan = []

    '''
    getPossibleActions return a list of tuple that represents the different actions the agent
    can execute in state s.
        return (logical_action, variables, primitive_action, new_agt_position)

    - logical_action is either Move, Push or Pull defined in Action.py
    - variables is the list of variable that the logical action take in argument
    - primitive_action is the action that we want to send to the server (e.g. "Push(E,E)")
    - new_agt_position is position of agent after executing the action
    '''

    def getPossibleActions(self, s: 'State'):
        possibleActions = []
        N = (-1,  0, 'N')
        S = ( 1,  0, 'S')
        E = ( 0,  1, 'E')
        W = ( 0, -1, 'W')
        agtFrom = s.findAgent(self.agt)
        # print(agtFrom, file=sys.stderr, flush=True)
        for action in self.actions:
            for dir in [N,S,E,W]:
                agtTo = (agtFrom[0]+dir[0], agtFrom[1]+dir[1])
                if action.name == "Move":
                    if action.checkPreconditions(s, [self.agt, agtFrom, agtTo]):
                        possibleActions.append((action, [self.agt, agtFrom, agtTo], "Move(" + dir[2] + ")", agtTo))
                elif action.name == "Push":
                    for second_dir in [N,S,E,W]:
                        boxFrom = agtTo #the agent will take the place of box
                        boxTo = (boxFrom[0]+second_dir[0], boxFrom[1]+second_dir[1])
                        box = s.findBox(boxFrom)
                        if box:
                            boxName = box.variables[0]
                            if action.checkPreconditions(s, [self.agt, agtFrom, boxName, boxFrom, boxTo, self.color]): # we also need box somehow
                                possibleActions.append((action,
                                                        [self.agt, agtFrom, boxName, boxFrom, boxTo, self.color],
                                                        "Push(" + dir[2] + "," + second_dir[2] + ")"))
                elif action.name == "Pull":
                    for second_dir in [N,S,E,W]:
                        boxFrom = (agtFrom[0]+second_dir[0], agtFrom[1]+second_dir[1])
                        box = s.findBox(boxFrom)
                        if box:
                            boxName = box.variables[0]
                            if action.checkPreconditions(s, [self.agt, agtFrom, agtTo, boxName, boxFrom, self.color]): # we also need box somehow
                                possibleActions.append((action,
                                                        [self.agt, agtFrom, agtTo, boxName, boxFrom, self.color],
                                                        "Pull(" + dir[2] + "," + second_dir[2] + ")"))
        shuffle(possibleActions)
        return possibleActions



    def plan(self, state:'State'):
        strategy = Strategy(state, self)
        strategy.plan()
