from collections import deque
from heapq import heapify, heappush, heappop
import sys

class Strategy:

    def __init__(self, state, agent, strategy='bfs'):
        self.state = state
        self.explored_states = set()
        self.agent = agent
        self.strategy = strategy
        self.goalNotFound = True
        self.expanded = set()

    def plan(self):
        if self.strategy == 'bfs':
            self.bfs()
        elif self.strategy == 'dfs':
            self.dfs()
        elif self.strategy == 'uniform':
            self.uniform()
        elif self.strategy == 'best-first':
            self.bestFirst()
        elif self.strategy == 'astar':
            self.astar()
        print('done')

    def uniform(self): #### LETS DISCUSS THIS ! I THINK WE SHOULD RESTRUCTURE ! it is not entoirelly correct
        frontier = []
        heappush(frontier, (self.state.cost, self.state))
        while len(frontier)> 0 and self.goalNotFound:
            s = heappop(frontier)[1]
            possibleActions = self.agent.getPossibleActions(s)
            for action in possibleActions:
                new_state = s.copy()

                action[0].execute(new_state, action[1])
                # print(new_state, file=sys.stderr, flush=True)
                new_state.parent = s
                new_state.last_action = {'action': action[0], 'params': action[1], 'message': action[2]}
                if self.agent.goal in new_state.atoms:
                    self.extract_plan(new_state)
                    goalNotFound = False

                    break
                if not new_state in frontier:  # not efficient at all should be replaced either by a set or by KB
                    heappush(frontier, (new_state.cost, new_state))


    def bfs(self):
        frontier = deque()
        frontier.append(self.state)
        self.goalNotFound = True
        while frontier != [] and self.goalNotFound:
            s = frontier.popleft()
            self.expanded.add(s)
            possibleActions = self.agent.getPossibleActions(s)
            #print(possibleActions, file=sys.stderr, flush=True)
            for action in possibleActions:
                new_state = s.copy()
                action[0].execute(new_state, action[1])
                print(new_state.atoms, file=sys.stderr, flush=True)
                new_state.parent = s
                new_state.last_action = { 'action': action[0], 'params': action[1], 'message': action[2] }
                if self.agent.goal in new_state.atoms:

                    self.extract_plan(new_state)
                    self.goalNotFound = False
                    break
                elif new_state not in frontier and new_state not in self.expanded: # not efficient at all should be replaced either by a set or by KB ## we should hash states as well
                    print(len(frontier), len(self.expanded), file=sys.stderr, flush=True)
                    frontier.append(new_state)


    def extract_plan(self, state):
        if state.parent:
            print(type(state.parent))
            self.agent.current_plan.append(state.last_action)
            self.extract_plan(state.parent)

        else:
            self.agent.current_plan.reverse()


