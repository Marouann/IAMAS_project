import sys
from strategy import Strategy
from random import shuffle
from atom import *
from action import *


class Agent:
    def __init__(self, name: 'str', position, goal: 'Atom', actions: '[Action]', color: 'str'):
        self.name = name
        #self.position = position
        self.goal = goal
        self.actions = actions
        self.color = color
        self.current_plan = []
        self.occupied = False

    '''
    getPossibleActions return a list of tuple that represents the different actions the agent
    can execute in state s.
        return (logical_action, variables, primitive_action, new_agt_position)

    - logical_action is either Move, Push or Pull defined in Action.py
    - variables is the list of variable that the logical action take in argument
    - primitive_action is the action that we want to send to the server (e.g. "Push(E,E)")
    - new_agt_position is position of agent after executing the action
    '''

    def assignGoal(self, goal):
        self.goal = goal
        self.occupied = True

    def getPossibleActions(self, s: 'State') -> '[Action]':
        possibleActions = []
        N = (-1, 0, 'N')
        S = (1, 0, 'S')
        E = (0, 1, 'E')
        W = (0, -1, 'W')
        #NO = (0,0, 'NO')
        agtFrom = s.findAgent(self.name)
        # print(agtFrom, file=sys.stderr, flush=True)
        for action in self.actions:
            for dir in [N, S, E, W]:
                agtTo = (agtFrom[0] + dir[0], agtFrom[1] + dir[1])
                if action.name == "Move":
                    if action.checkPreconditions(s, [self.name, agtFrom, agtTo]):
                        possibleActions.append((action, [self.name, agtFrom, agtTo], "Move(" + dir[2] + ")", agtTo))
                elif action.name == "Push":
                    for second_dir in [N, S, E, W]:
                        boxFrom = agtTo  # the agent will take the place of box
                        boxTo = (boxFrom[0] + second_dir[0], boxFrom[1] + second_dir[1])
                        box = s.findBox(boxFrom)
                        if box:
                            boxName = box.variables[0]
                            if action.checkPreconditions(s, [self.name, agtFrom, boxName, boxFrom, boxTo,
                                                             self.color]):  # we also need box somehow
                                possibleActions.append((action,
                                                        [self.name, agtFrom, boxName, boxFrom, boxTo, self.color],
                                                        "Push(" + dir[2] + "," + second_dir[2] + ")"))
                elif action.name == "Pull":
                    for second_dir in [N, S, E, W]:
                        boxFrom = (agtFrom[0] + second_dir[0], agtFrom[1] + second_dir[1])
                        box = s.findBox(boxFrom)
                        if box:
                            boxName = box.variables[0]
                            if action.checkPreconditions(s, [self.name, agtFrom, agtTo, boxName, boxFrom,
                                                             self.color]):  # we also need box somehow
                                possibleActions.append((action,
                                                        [self.name, agtFrom, agtTo, boxName, boxFrom, self.color],
                                                        "Pull(" + dir[2] + "," + second_dir[2] + ")"))
                elif action.name == 'NoOp':
                                possibleActions.append((action, [self.name, agtFrom], 'NoOp'))
        shuffle(possibleActions)

        return possibleActions

    def plan(self, state: 'State'):
        strategy = Strategy(state, self)
        strategy.plan()
