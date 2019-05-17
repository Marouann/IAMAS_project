from collections import deque
from numpy import inf
from state import State
from heapq import heapify, heappush, heappop
from agent import *
from multiprocessing import Event

from Heuristics.heuristics import GoalCount, DistanceBased, ActionPriority, DynamicHeuristics
import sys

INF = inf


class Strategy:
    """"Strategy class is responsible for the planning and searching strategies"""

    def __init__(self, state: 'State', agent: 'Agent',
                 strategy='best-first',
                 heuristics='Distance',
                 metrics='Real',
                 multi_goal=False,
                 max_depth=None,
                 quit_event=Event(),
                 found_event=Event()):

        self.state = state
        self.agent = agent
        self.strategy = strategy
        self.heuristics = heuristics
        self.metrics = metrics
        self.multi_goal = multi_goal
        self.max_depth = max_depth
        self.goal_found = False
        self.expanded = set()  # stores expanded states
        self.async_mode = False
        self.quit_event = quit_event
        self.found_event = found_event

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
                self.a_star(self.quit_event, self.found_event)
            elif self.strategy == 'IDA':
                self.IDA(self.quit_event, self.found_event)

    def async_plan(self):
        if not self.__is_goal__(self.agent, self.state, self.multi_goal) and self.agent.goal is not None:
            if self.strategy == 'astar':
                self.a_star(self.quit_event, self.found_event)
            elif self.strategy == 'IDA':
                self.IDA(self.quit_event, self.found_event)

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
                state_ = s.create_child(action, cost=1)
                self.__is_goal__(self.agent, state_, multi_goal=self.multi_goal)

                if not self.goal_found and self.max_depth is not None and s.cost < self.max_depth:
                    if state_ not in frontier and state_ not in self.expanded and not self.goal_found:
                        # print(len(frontier), len(self.expanded), file=sys.stderr, flush=True)
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
                                GoalCount.h(self.state, scaler=5)

        frontier = list()
        self.expanded = set()
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

    def a_star(self, quit_event, found_event):
        self.state.reset_state()
        self.agent.reset_plan()
        print('Solving with A*', self.heuristics, self.metrics, file=sys.stderr, flush=True)
        if self.heuristics == 'GoalCount':
            self.state.h_cost = GoalCount.h(self.state)
        elif self.heuristics == 'Distance':
            self.state.h_cost = DistanceBased.h(self.state, self.agent, metrics=self.metrics)
        elif self.heuristics == 'Complex':
            self.state.h_cost = DistanceBased.h(self.state, self.agent, metrics=self.metrics) + \
                                ActionPriority.h(self.state, scaler=10) + GoalCount.h(self.state, 150)
        elif self.heuristics == 'Dynamic':
            if len(self.state.rigid_atoms) > 150000:
                self.decay = 100
                self.bias = 5
                self.distance_scaler = 3
                self.action_scaler = 1.5
            else:
                self.decay = 1000
                self.bias = 1.5
                self.distance_scaler = 1.2
                self.action_scaler = 5
            self.state.h_cost = DynamicHeuristics.h(self.state, self.agent, metrics=self.metrics,
                                                    action_scaler=self.action_scaler, decay=self.decay,
                                                    distance_scaler=self.distance_scaler)

        frontier = list()
        heappush(frontier, self.state)
        while frontier and not self.goal_found and not quit_event.is_set():
            s = heappop(frontier)
            self.expanded.add(s)
            self.__is_goal__(self.agent, s)
            if self.goal_found and not quit_event.is_set():
                print('A* found a solution', file=sys.stderr)
                found_event.set()
                return True
            if not self.goal_found and not quit_event.is_set():
                for action in self.agent.getPossibleActions(s):
                    state_ = s.create_child(action, cost=1)
                    if self.heuristics == 'GoalCount':
                        state_.h_cost = GoalCount.h(state_)
                    elif self.heuristics == 'Distance':
                        state_.h_cost = DistanceBased.h(state_, self.agent, metrics=self.metrics)
                    elif self.heuristics == 'Complex':
                        state_.h_cost = DistanceBased.h(state_, self.agent, metrics=self.metrics) + \
                                        ActionPriority.h(state_, scaler=10) + GoalCount.h(self.state, 150)

                    elif self.heuristics == 'Dynamic':
                        state_.h_cost = DynamicHeuristics.h(state_, self.agent, metrics=self.metrics,
                                                            action_scaler=self.action_scaler, decay=self.decay,
                                                            distance_scaler=self.distance_scaler)
                        self.evaluate_cost(state_, bias=self.bias)

                    if state_ not in frontier and state_ not in self.expanded:
                        heappush(frontier, state_)
                        heapify(frontier)
        if not quit_event.is_set():
            found_event.set()
            return False

    def IDA(self, quit_event, found_event, h_function=DistanceBased):
        print('Solving with IDA*', self.heuristics, self.metrics, file=sys.stderr, flush=True)

        def search(state, limit):
            if found_event.is_set():
                return
            state.h_cost = h_function.h(state, self.agent, metrics=self.metrics)
            if state.__total_cost__() > limit:
                return state.__total_cost__()

            minimum = INF
            for action in self.agent.getPossibleActions(state):
                s = state.create_child(action, cost=1)
                if not quit_event.is_set():
                    self.__is_goal__(self.agent, s)
                    if self.goal_found:
                        print('IDA', 'solution is found', file=sys.stderr)
                        found_event.set()
                        return True
                temporary = search(s, limit)
                if temporary < minimum and (s, s.cost) not in self.expanded:
                    minimum = temporary
                    self.expanded.add((s, s.cost))
            return minimum

        ##IDA starts here
        self.state.h_cost = h_function.h(self.state, self.agent, metrics=self.metrics)
        threshold = self.state.h_cost
        while not self.goal_found and not quit_event.is_set():
            self.state.reset_state()
            temp = search(self.state, threshold)
            if self.goal_found:
                print('IDA', 'solution is found', file=sys.stderr)
                found_event.set()
                return True
            if temp == INF and not self.goal_found:
                print('IDA', 'solution is not found', file=sys.stderr)
                found_event.set()
                return False
            elif quit_event.is_set():
                print('IDA is terminated', file=sys.stderr)
                return False
            threshold = temp
        if not quit_event.is_set():
            print('IDA', 'solution is not found', file=sys.stderr)
            return False

    def extract_plan(self, state: 'State'):
        if state:
            if not self.multi_goal and self.agent.goal in state.atoms:
                self.agent.reset_plan()

            # print(state.cost, state.h_cost, state.__total_cost__(), file=sys.stderr, flush = True)
            self.agent.current_plan.append(state.last_action)
            self.extract_plan(state.parent)
        else:
            self.agent.current_plan = self.agent.current_plan[:-1]
            self.agent.current_plan.reverse()

    def evaluate_cost(self, new_state: 'State', bias=5):
        if new_state in self.expanded:
            s = set()
            s.add(new_state)
            union = self.expanded.union(s)
            old_state = union.pop()

            # print('UNION', new_state.__total_cost__(), old_state.__total_cost__(), file=sys.stderr, flush = True)
            if new_state.__total_cost__() + bias < old_state.__total_cost__():
                # print('YESS', file=sys.stderr, flush = True)
                self.expanded.remove(old_state)

    def __is_goal__(self, agent: 'Agent', state: 'State', multi_goal=False) -> 'bool':
        if not multi_goal:
            if agent.goal in state.atoms and not self.goal_found:
                self.extract_plan(state)
                self.goal_found = True
                # print('Plan found for agent : ' + str(agent.name) + ' with goal : ' + str(agent.goal) + '\n',
                #     file=sys.stderr, flush=True)  # print out
                for item in agent.current_plan:
                    print(item['message'], item['params'], file=sys.stderr, flush=True)
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

            return is_goal
