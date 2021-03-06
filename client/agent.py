from strategy import Strategy
from action import *
from Tracker import Tracker
from multiprocessing import Process, Event
from time import sleep
import random

STRATEGY = 'astar' # [ 'uniform', 'bfs', 'dfs', 'best' , 'astar', 'ida']
HEURISTICS = 'Tie Breaking'  # ['Distance', 'Dynamic', 'Tie Breaking']
METRICS = 'Real' #['Manhattan', 'Euclidean', 'Real']

STRATEGY_GHOST = 'astar'
HEURISTICS_GHOST = 'Tie Breaking'


ASYNC = False
# BOUND = 1750 #['None', integer] ## replaced by agent attribute



class Agent:
    def __init__(self, name: 'str', position, goal: 'Atom', actions: '[Action]', color: 'str'):
        self.name = name
        self.goal = goal
        self.goal_details = None
        self.actions = actions
        self.color = color
        self.current_plan = []
        self.occupied = False
        self.status = None
        self.tracker = None
        self.ghostmode = False
        self.bound = 1750

    '''
    getPossibleActions return a list of tuple that represents the different actions the agent
    can execute in state s.
        return (logical_action, variables, primitive_action, new_agt_position)

    - logical_action is either Move, Push or Pull defined in Action.py
    - variables is the list of variable that the logical action take in argument
    - primitive_action is the action that we want to send to the server (e.g. "Push(E,E)")
    - new_agt_position is position of agent after executing the action
    - priority of the action.
    '''

    def assignGoal(self, goal, goal_details):
        self.goal = goal
        self.goal_details = goal_details
        self.occupied = True

    def getPossibleActions(self, s: 'State', ghostmode:'bool'=False) -> '[Action]':
        possibleActions = list()
        N = (-1, 0, 'N')
        S = (1, 0, 'S')
        E = (0, 1, 'E')
        W = (0, -1, 'W')
        agtFrom = s.find_agent(self.name)

        for action in self.actions:
            for dir in [N, S, E, W]:
                agtTo = (agtFrom[0] + dir[0], agtFrom[1] + dir[1])

                if action.name == "Move":
                    if action.checkPreconditions(s, [self.name, agtFrom, agtTo], ghostmode=ghostmode):
                        possibleActions.append((action, [self.name, agtFrom, agtTo], "Move(" + dir[2] + ")", agtTo, 0))

                elif action.name == "Push":
                    for second_dir in [N, S, E, W]:
                        boxFrom = agtTo  # the agent will take the place of box
                        boxTo = (boxFrom[0] + second_dir[0], boxFrom[1] + second_dir[1])
                        box = s.find_box(boxFrom, self.color)
                        # if (box and not ghostmode) or (ghostmode and box and box.variables[0] == boxOfGoal)
                        if box:
                            boxName = box.variables[0]
                            if boxFrom != boxTo and boxTo != agtFrom and agtFrom != boxFrom:
                                if action.checkPreconditions(s, [self.name, agtFrom, boxName, boxFrom, boxTo,
                                                                 self.color], ghostmode=ghostmode):  # we also need box somehow
                                    possibleActions.append((action,
                                                            [self.name, agtFrom, boxName, boxFrom, boxTo, self.color],
                                                            "Push(" + dir[2] + "," + second_dir[2] + ")",
                                                            boxFrom,
                                                            0.7))
                elif action.name == "Pull":
                    for second_dir in [N, S, E, W]:
                        boxFrom = (agtFrom[0] + second_dir[0], agtFrom[1] + second_dir[1])
                        box = s.find_box(boxFrom, self.color)
                        if box:
                            boxName = box.variables[0]
                            if agtFrom != agtTo and agtTo != boxFrom and boxFrom != agtFrom:
                                if action.checkPreconditions(s, [self.name, agtFrom, agtTo, boxName, boxFrom,
                                                                 self.color], ghostmode=ghostmode):  # we also need box somehow
                                    possibleActions.append((action,
                                                            [self.name, agtFrom, agtTo, boxName, boxFrom, self.color],
                                                            "Pull(" + dir[2] + "," + second_dir[2] + ")",
                                                            agtTo,
                                                            0.7))
                elif action.name == 'NoOp':
                    possibleActions.append((action, [self.name, agtFrom], 'NoOp', agtFrom, 0.7))

        return possibleActions

    def reset_plan(self):
        self.current_plan = []

    def update_tracker(self, state: 'State'):
        self.tracker = Tracker(state.find_agent(self.name))
        self.tracker.estimate(state)


    def plan(self, state: 'State', strategy=STRATEGY,
             multi_goal=False, max_depth=None,
             async_mode=ASYNC, metrics =METRICS, heuristics=HEURISTICS):
        max_depth = self.bound

        print("Agent:", self.name,  file=sys.stderr)
        print("Planning for goal:", self.goal_details, file=sys.stderr)
        print("Bound is ", self.bound, file=sys.stderr)
        print("Ghost mode is on", self.ghostmode, file=sys.stderr)
        if not self.ghostmode:
            strategy = Strategy(state, self,
                                strategy=STRATEGY,
                                heuristics=heuristics,
                                metrics=metrics,
                                multi_goal=multi_goal,
                                max_depth=max_depth,
                                ghostmode=self.ghostmode)
        else:
            strategy = Strategy(state, self,
                                strategy=STRATEGY_GHOST,
                                heuristics=HEURISTICS_GHOST,
                                metrics=metrics,
                                multi_goal=multi_goal,
                                max_depth=max_depth,
                                ghostmode=self.ghostmode)

        strategy.plan()
