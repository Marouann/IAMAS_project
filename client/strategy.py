from collections import deque

class Strategy:

    def __init__(self, state, agent, strategy='bfs'):
        self.state = state
        self.agent = agent
        self.strategy = strategy


    def plan(self):
        if self.strategy == 'bfs':
            self.bfs()
        elif self.strategy == 'dfs':
            self.dfs()
        elif self.strategy == 'best-first':
            self.bestFirst()
        elif self.strategy == 'astar':
            self.astar()


    def bfs(self):
        frontier = deque()
        frontier.append(self.state)
        goalNotFound = True
        while frontier != [] and goalNotFound:
            s = frontier.popleft(0)
            possibleActions = self.agent.getPossibleActions(s)
            # print(possibleActions, file=sys.stderr, flush=True)
            for action in possibleActions:
                new_state = s.copy()

                action[0].execute(new_state, action[1])
                # print(new_state, file=sys.stderr, flush=True)
                new_state.parent = s
                new_state.last_action = { 'action': action[0], 'params': action[1], 'message': action[2] }
                if self.agent.goal in new_state.atoms.kb:

                    goalNotFound = False
                    self.extract_plan(new_state)
                    break
                if not new_state in frontier: # not efficient at all should be replaced either by a set or by KB
                    frontier.append(new_state)


    def extract_plan(self, state):
        if state.parent:
            self.agent.current_plan.append(state.last_action)
            self.extract_plan(state.parent)
        else:
            self.agent.current_plan.reverse()
