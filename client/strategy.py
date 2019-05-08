from collections import deque
from state import State
from heapq import heapify, heappush, heappop
from agent import *

from Heuristics.heuristics import GoalCount, DistanceBased, ActionPriority
import sys


class Strategy:
    """"Strategy class is responsible for the planning and searching strategies"""
    def __init__(self, state: 'State', agent: 'Agent',
                 strategy='astar',
                 heuristics='Complex',
                 metrics='Real',
                 multi_goal=False):

        self.state = state
        self.agent = agent
        self.strategy = strategy
        self.heuristics = heuristics
        self.metrics = metrics
        self.multi_goal = multi_goal

        self.goal_found = False
        self.expanded = set()  # stores expanded states

    def plan(self):
        if not self.__is_goal__(self.agent, self.state, self.multi_goal) and self.agent.goal is not None:
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
            possible_actions = self.agent.getPossibleActions(s)

            for action in possible_actions:
                state_ = s.create_child(action, cost=1)
                self.__is_goal__(self.agent, state_)
                if not self.goal_found:
                    if state_ not in frontier and state_ not in self.expanded:
                        heappush(frontier, state_)
                        heapify(frontier)

    def bfs(self):
        frontier = deque()
        frontier.append(self.state)

        while frontier and not self.goal_found:
            s = frontier.popleft()
            self.expanded.add(s)
            possible_actions = self.agent.getPossibleActions(s)

            for action in possible_actions:
                state_ = s.create_child(action)
                self.__is_goal__(self.agent, state_,multi_goal=self.multi_goal)
                if not self.goal_found:
                    if state_ not in frontier and state_ not in self.expanded:
                        frontier.append(state_)

    def dfs(self):
        frontier = list()
        frontier.append(self.state)

        while frontier and not self.goal_found:
            s = frontier.pop()
            self.expanded.add(s)
            possible_actions = self.agent.getPossibleActions(s)

            for action in possible_actions:
                state_ = s.create_child(action)
                self.__is_goal__(self.agent, state_)
                if not self.goal_found:
                    if state_ not in frontier and state_ not in self.expanded:
                        frontier.append(state_)

    def best_first(self):
        print('Solving with best-first', self.heuristics, self.metrics, file=sys.stderr, flush=True)
        if self.heuristics == 'GoalCount':
            self.state.h_cost = GoalCount.h(self.state)
        elif self.heuristics == 'Distance':
            self.state.h_cost = DistanceBased.h(self.state, self.agent, metrics=self.metrics)
        elif self.heuristics == 'Complex':
            self.state.h_cost = DistanceBased.h(self.state, self.agent, metrics=self.metrics) + \
                            ActionPriority.h(self.state, scaler=10)

        frontier = list()
        self.expanded.clear()
        heappush(frontier, self.state)

        while frontier and not self.goal_found:
            s = heappop(frontier)
            self.expanded.add(s)
            for action in self.agent.getPossibleActions(s):
                state_ = s.create_child(action, cost=0)
                self.__is_goal__(self.agent, state_)
                if not self.goal_found:
                    if state_ not in frontier and state_ not in self.expanded:
                        if self.heuristics == 'GoalCount':
                            state_.h_cost = GoalCount.h(state_)
                        elif self.heuristics == 'Distance':
                            state_.h_cost = DistanceBased.h(state_, self.agent, metrics=self.metrics)
                        elif self.heuristics == 'Complex':
                            state_.h_cost = DistanceBased.h(state_, self.agent, metrics=self.metrics) + \
                                            ActionPriority.h(state_, scaler=10)
                        heappush(frontier, state_)
                        heapify(frontier)

    def a_star(self):
        print('Solving with A*', self.heuristics, self.metrics, file=sys.stderr, flush=True)
        if self.heuristics == 'GoalCount':
            self.state.h_cost = GoalCount.h(self.state)
        elif self.heuristics == 'Distance':
            self.state.h_cost = DistanceBased.h(self.state, self.agent, metrics=self.metrics)
        elif self.heuristics == 'Complex':
            self.state.h_cost = DistanceBased.h(self.state, self.agent, metrics=self.metrics) + \
                            ActionPriority.h(self.state, scaler=10)

        frontier = list()
        self.expanded.clear()
        heappush(frontier, self.state)

        while frontier and not self.goal_found:
            s = heappop(frontier)
            self.expanded.add(s)
            for action in self.agent.getPossibleActions(s):
                state_ = s.create_child(action, cost=1)
                self.__is_goal__(self.agent, state_)
                if not self.goal_found:
                    if state_ not in frontier and state_ not in self.expanded:
                        if self.heuristics == 'GoalCount':
                            state_.h_cost = GoalCount.h(state_)
                        elif self.heuristics == 'Distance':
                            state_.h_cost = DistanceBased.h(state_, self.agent, metrics=self.metrics)
                        elif self.heuristics == 'Complex':
                            state_.h_cost = DistanceBased.h(state_, self.agent, metrics=self.metrics) + \
                                            ActionPriority.h(state_, scaler=10)
                        heappush(frontier, state_)
                        heapify(frontier)

    def extract_plan(self, state: 'State'):
        if state:
            self.agent.current_plan.append(state.last_action)
            self.extract_plan(state.parent)
        else:
            self.agent.current_plan = self.agent.current_plan[:-1]
            self.agent.current_plan.reverse()

    def __is_goal__(self, agent: 'Agent', state: 'State', multi_goal=False) -> 'bool':
        if not multi_goal:
            if agent.goal in state.atoms and not self.goal_found:
                self.extract_plan(state)
                self.goal_found = True
                print('Plan found for agent : ' + str(agent.name) + ' with goal : ' + str(agent.goal) + '\n',
                      file=sys.stderr, flush=True)  # print out

                return True
            return False
        else:
            is_goal = True
            for goal in agent.goal:
                if goal not in state.atoms:
                    is_goal = False
            if is_goal:
                self.goal_found = True
                self.extract_plan(state)
                print('Plan found for agent : ' + str(agent.name) + ' with goal : ',
                      file=sys.stderr, flush=True)
                for goal in agent.goal:
                    print(goal, file=sys.stderr)
                print('Plan: ', agent.current_plan, file=sys.stderr )
            return is_goal
