from strategy import Strategy
from action import *
from Tracker import Tracker
from multiprocessing import Process, Event
from time import sleep

STRATEGY = 'astar'
HEURISTICS = 'Distance'
METRICS = 'Real'
ASYNC = True



class Agent:
    def __init__(self, name: 'str', position, goal: 'Atom', actions: '[Action]', color: 'str'):
        self.name = name
        # self.position = position
        self.goal = goal
        self.goal_details = None
        self.actions = actions
        self.color = color
        self.current_plan = []
        self.occupied = False
        self.status = None
        self.tracker = None

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

    def getPossibleActions(self, s: 'State') -> '[Action]':
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
                    if action.checkPreconditions(s, [self.name, agtFrom, agtTo]):
                        possibleActions.append((action, [self.name, agtFrom, agtTo], "Move(" + dir[2] + ")", agtTo, 0))
                elif action.name == "Push":
                    for second_dir in [N, S, E, W]:
                        boxFrom = agtTo  # the agent will take the place of box
                        boxTo = (boxFrom[0] + second_dir[0], boxFrom[1] + second_dir[1])
                        box = s.find_box(boxFrom)
                        if box:
                            boxName = box.variables[0]
                            if action.checkPreconditions(s, [self.name, agtFrom, boxName, boxFrom, boxTo,
                                                             self.color]):  # we also need box somehow
                                possibleActions.append((action,
                                                        [self.name, agtFrom, boxName, boxFrom, boxTo, self.color],
                                                        "Push(" + dir[2] + "," + second_dir[2] + ")",
                                                        boxFrom,
                                                        2))
                elif action.name == "Pull":
                    for second_dir in [N, S, E, W]:
                        boxFrom = (agtFrom[0] + second_dir[0], agtFrom[1] + second_dir[1])
                        box = s.find_box(boxFrom)
                        if box:
                            boxName = box.variables[0]
                            if action.checkPreconditions(s, [self.name, agtFrom, agtTo, boxName, boxFrom,
                                                             self.color]):  # we also need box somehow
                                possibleActions.append((action,
                                                        [self.name, agtFrom, agtTo, boxName, boxFrom, self.color],
                                                        "Pull(" + dir[2] + "," + second_dir[2] + ")",
                                                        agtTo,
                                                        2.5))
                elif action.name == 'NoOp':
                    possibleActions.append((action, [self.name, agtFrom], 'NoOp', agtFrom, 3))
        possibleActions.sort(key=lambda tup: tup[4])

        return possibleActions

    def reset_plan(self):
        self.current_plan = []

    def update_tracker(self, state: 'State'):
        self.tracker = Tracker(state.find_agent(self.name))
        self.tracker.estimate(state)

    def plan(self, state: 'State', strategy=STRATEGY,
             multi_goal=False, max_depth=None,
             async_mode=ASYNC):
        if not async_mode:
            print("Agent:", self.name, file=sys.stderr)
            print("Planning for goal:", self.goal_details, file=sys.stderr)
            strategy = Strategy(state, self, strategy=strategy, heuristics=HEURISTICS, metrics=METRICS,
                                multi_goal=multi_goal, max_depth=max_depth)
            strategy.plan()
        else:
            found_event = Event()
            quit_event = Event()


            print('STRATEGY::','Agent', self.name, file=sys.stderr, flush=True)
            print('STRATEGY::', 'ASYNC Planning for goal:', self.goal_details, file=sys.stderr, flush=True)

            #### STRATEGY SPECIFICATIONS
            strategies = list()
            strategies.append(Strategy(state, self, strategy='astar', heuristics='Dynamic',
                                       metrics='Real', found_event=found_event, quit_event=quit_event))
            strategies.append(Strategy(state, self, strategy='IDA', heuristics='Distance',
                                       metrics='Real', found_event=found_event, quit_event=quit_event))

            #### PROCESSES SPECIFICATION
            processes = list()
            process = Process(target=strategies[0].async_plan(), name='A* Process', group=None)
            process.start()
            print('STRATEGY::', process.name, 'started', file=sys.stderr, flush = True)
            processes.append(process)
            process = Process(target=strategies[0].async_plan(), name='IDA* Process', group=None)
            process.start()
            print('STRATEGY::', process.name, 'started', file=sys.stderr, flush=True)
            processes.append(process)
            found_event.wait() #wait for the event

            print('STRATEGY::','Found the solution', file=sys.stderr, flush=True)
            quit_event.set()
            print('STRATEGY::', 'Set QUIT EVENT to the TRUE', file=sys.stderr, flush=True)
            for p in processes:
                print('STRATEGY::', p.name, 'terminated', file=sys.stderr, flush=True)
                p.terminate()
