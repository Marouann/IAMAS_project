import sys

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

    def getPossibleActions(self, s):
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
        return possibleActions



    def plan(self, state):
        frontier = []
        frontier.append(state)
        goalNotFound = True
        while frontier != [] and goalNotFound:
            s = frontier.pop(0)
            print(len(frontier), file=sys.stderr, flush=True)
            possibleActions = self.getPossibleActions(s)
            # print(possibleActions, file=sys.stderr, flush=True)
            for action in possibleActions:
                new_state = s.copy()

                action[0].execute(new_state, action[1])
                # print(new_state, file=sys.stderr, flush=True)
                new_state.parent = s
                new_state.last_action = { 'action': action[0], 'params': action[1], 'message': action[2] }
                if self.goal in new_state.atoms:

                    goalNotFound = False
                    self.extract_plan(new_state)
                    break
                if not new_state in frontier:
                    frontier.append(new_state)

    def extract_plan(self, state):
        if state.parent:
            self.current_plan.append(state.last_action)
            self.extract_plan(state.parent)
        else:
            self.current_plan.reverse()
