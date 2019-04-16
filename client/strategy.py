from collections import deque
from state import State
from heapq import heapify, heappush, heappop

from Heuristics.heuristics import GoalCount
import sys


class Strategy:

    def __init__(self, state, agent, strategy='bfs', heuristics=None):
        self.state = state
        self.explored_states = set()
        self.agent = agent
        self.strategy = strategy
        self.heuristics = heuristics
        self.goal_found = False
        self.expanded = set()

    def plan(self):
        if self.strategy == 'bfs':
            self.bfs()
        elif self.strategy == 'dfs':
            self.dfs()
        elif self.strategy == 'uniform':
            self.uniform()
        elif self.strategy == 'best-first':
            self.best_first()
        elif self.strategy == 'astar':
            self.a_star()

    def uniform(self):
        frontier = list()
        heappush(frontier, self.state)

        while len(frontier) > 0 and not self.goal_found:
            s = heappop(frontier)
            self.expanded.add(s)
            possibleActions = self.agent.getPossibleActions(s)

            for action in possibleActions:
                state_ = s.copy()
                action[0].execute(state_, action[1])
                state_.parent = s
                state_.cost += 1
                state_.last_action = {'action': action[0], 'params': action[1], 'message': action[2]}
                self.__is_goal__(self.agent, state_)

                if state_ not in frontier and state_ not in self.expanded and not self.goal_found:
                    heappush(frontier, state_)
                    heapify(frontier)

    def bfs(self):
        frontier = deque()
        frontier.append(self.state)

        while len(frontier) > 0 and not self.goal_found:
            s = frontier.popleft()
            self.expanded.add(s)
            possibleActions = self.agent.getPossibleActions(s)

            for action in possibleActions:
                state_ = s.copy()
                action[0].execute(state_, action[1])
                state_.parent = s
                state_.last_action = {'action': action[0], 'params': action[1], 'message': action[2]}
                self.__is_goal__(self.agent, state_)

                if state_ not in frontier and state_ not in self.expanded and not self.goal_found:
                    frontier.append(state_)

    def dfs(self):
        frontier = list()
        frontier.append(self.state)

        while len(frontier) > 0 and not self.goal_found:
            s = frontier.pop()
            self.expanded.add(s)
            possibleActions = self.agent.getPossibleActions(s)

            for action in possibleActions:
                state_ = s.copy()
                action[0].execute(state_, action[1])
                state_.parent = s
                state_.last_action = {'action': action[0], 'params': action[1], 'message': action[2]}
                self.__is_goal__(self.agent, state_)

                if state_ not in frontier and state_ not in self.expanded and not self.goal_found:
                    frontier.append(state_)

    def best_first(self):
        frontier = list()
        heappush(frontier, self.state)

        while len(frontier) > 0 and not self.goal_found:
            s = heappop(frontier)
            self.expanded.add(s)
            possibleActions = self.agent.getPossibleActions(s)

            for action in possibleActions:
                state_ = s.copy()
                action[0].execute(state_, action[1])
                state_.parent = s
                state_.last_action = {'action': action[0], 'params': action[1], 'message': action[2]}
                state_.cost = GoalCount(self.state, self.state.goals).h(state_)
                if not self.goal_found and not self.__is_goal__(self.agent, state_):
                    if state_ not in frontier and state_ not in self.expanded and not self.goal_found:
                        # print(len(frontier), len(self.expanded), file=sys.stderr, flush=True)
                        heappush(frontier, state_)
                        heapify(frontier)

    def a_star(self):
        pass

    def extract_plan(self, state):
        if state:
            self.agent.current_plan.append(state.last_action)
            self.extract_plan(state.parent)
        else:
            self.agent.current_plan = self.agent.current_plan[:-1]
            self.agent.current_plan.reverse()

    def __is_goal__(self, agent, state):
        if agent.goal in state.atoms:
            self.extract_plan(state)
            self.goal_found = True
            print(str(agent.agt) + ' : ' + str(agent.goal) + ' ' + str(agent.current_plan) + '\n', file=sys.stderr, flush=True) # print out

            return True
        return False
