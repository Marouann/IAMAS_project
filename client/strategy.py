from collections import deque
from state import State
from heapq import heapify, heappush, heappop
from Tracker import *
from utils import level_adjacency

from agent import *

from Heuristics.heuristics import GoalCount, DistanceBased
import sys


class Strategy:
    """"Strategy class is responsible for the planning and searching strategies"""
    def __init__(self, state: 'State', agent: 'Agent', strategy='astar', heuristics='Distance', metrics='Real'):
        self.state = state
        self.agent = agent
        self.strategy = strategy
        self.heuristics = heuristics
        self.metrics = metrics
        self.goal_found = False

        self.expanded = set()  # stores expanded states

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
        elif self.strategy == 'ida':
            self.IDA()

    def uniform(self):
        frontier = list()
        heappush(frontier, self.state)

        while len(frontier) > 0 and not self.goal_found:
            s = heappop(frontier)
            self.expanded.add(s)
            possible_actions = self.agent.getPossibleActions(s)

            for action in possible_actions:
                state_ = s.create_child(action, cost=1)
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
            possible_actions = self.agent.getPossibleActions(s)

            for action in possible_actions:
                state_ = s.create_child(action)
                self.__is_goal__(self.agent, state_)

                if state_ not in frontier and state_ not in self.expanded and not self.goal_found:
                    frontier.append(state_)

    def dfs(self):
        frontier = list()
        frontier.append(self.state)

        while len(frontier) > 0 and not self.goal_found:
            s = frontier.pop()
            self.expanded.add(s)
            possible_actions = self.agent.getPossibleActions(s)

            for action in possible_actions:
                state_ = s.create_child(action)
                self.__is_goal__(self.agent, state_)

                if state_ not in frontier and state_ not in self.expanded and not self.goal_found:
                    frontier.append(state_)

    def best_first(self):
        print('Solving with best-first', self.heuristics, self.metrics, file=sys.stderr, flush=True)
        if self.heuristics == 'GoalCount':
            self.state.h_cost = GoalCount(self.state, self.state.goals).h(self.state)
        elif self.heuristics == 'Distance':
            self.state.h_cost = DistanceBased(self.state, self.state.goals).h(self.state, self.agent, metrics=self.metrics)

        frontier = list()
        heappush(frontier, self.state)

        while frontier and not self.goal_found:
            s = heappop(frontier)
            self.expanded.add(s)
            possible_actions = self.agent.getPossibleActions(s)

            for action in possible_actions:
                state_ = s.create_child(action)

                if self.heuristics == 'GoalCount':
                    state_.h_cost = GoalCount(self.state, self.state.goals).h(state_)
                elif self.heuristics == 'Distance':
                    state_.h_cost = DistanceBased(self.state, self.state.goals).h(state_, self.agent, metrics=self.metrics)

                self.__is_goal__(self.agent, state_)
                if not self.goal_found and not self.__is_goal__(self.agent, state_):
                    if state_ not in frontier and state_ not in self.expanded and not self.goal_found:
                        # print(len(frontier), len(self.expanded), file=sys.stderr, flush=True)
                        heappush(frontier, state_)
                        heapify(frontier)

    def a_star(self):
        print('Solving with A*', self.heuristics, self.metrics, file=sys.stderr, flush=True)
        if self.heuristics == 'GoalCount':
            self.state.h_cost = GoalCount(self.state, self.state.goals).h(self.state)
        elif self.heuristics == 'Distance':
            self.state.h_cost = DistanceBased(self.state, self.state.goals).h(self.state, self.agent, metrics=self.metrics)

        frontier = list()
        heappush(frontier, self.state)

        while len(frontier) > 0 and not self.goal_found:
            s = heappop(frontier)
            self.expanded.add(s)
            possible_actions = self.agent.getPossibleActions(s)

            for action in possible_actions:
                state_ = s.create_child(action, cost=1)

                if self.heuristics == 'GoalCount':
                    state_.h_cost = GoalCount(self.state, self.state.goals).h(state_)
                elif self.heuristics == 'Distance':
                    state_.h_cost = DistanceBased(self.state, self.state.goals).h(state_, self.agent, metrics=self.metrics)

                self.__is_goal__(self.agent, state_)
                if not self.goal_found and not self.__is_goal__(self.agent, state_):
                    if state_ not in frontier and state_ not in self.expanded and not self.goal_found:
                        # print(len(frontier), len(self.expanded), file=sys.stderr, flush=True)
                        print(state_.h_cost, file=sys.stderr, flush=True)
                        # print(state_.cost, file=sys.stderr, flush=True)
                        heappush(frontier, state_)
                        heapify(frontier)

    def extract_plan(self, state: 'State'):
        if state:
            self.agent.current_plan.append(state.last_action)
            self.extract_plan(state.parent)
        else:
            self.agent.current_plan = self.agent.current_plan[:-1]
            self.agent.current_plan.reverse()

    def __is_goal__(self, agent: 'Agent', state: 'State') -> 'bool':
        if agent.goal in state.atoms:
            self.extract_plan(state)
            self.goal_found = True
            print('Plan found for agent : ' + str(agent.name) + ' with goal : ' + str(agent.goal) + '\n',
                  file=sys.stderr, flush=True)  # print out

            return True
        return False
