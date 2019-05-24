from collections import deque
from numpy import inf, exp
from state import State
from heapq import heapify, heappush, heappop
from agent import *
from multiprocessing import Event

from Heuristics.heuristics import TieBreaking, DistanceBased, DynamicHeuristics
import sys

INF = inf


class Strategy:
    """"Strategy class is responsible for the planning and searching strategies"""

    def __init__(self, state: 'State', agent: 'Agent',
                 strategy,
                 heuristics,
                 metrics,
                 multi_goal=False,
                 max_depth=None,
                 ghostmode=False,
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
        self.ghostmode = ghostmode
        self.async_mode = False
        self.quit_event = quit_event
        self.found_event = found_event

    def plan(self):
        if not self.__is_goal__(self.agent, self.state, multi_goal=self.multi_goal) and self.agent.goal is not None:
            if self.strategy == 'bfs':
                self.bfs()
            elif self.strategy == 'dfs':
                self.dfs()
            elif self.strategy == 'uniform':
                self.uniform()
            elif self.strategy == 'best':
                self.best_first()
            elif self.strategy == 'astar':
                self.a_star()
            elif self.strategy == 'ida':
                self.IDA()

    def async_plan(self):
        if not self.__is_goal__(self.agent, self.state) and self.agent.goal is not None:
            if self.strategy == 'astar':
                self.a_star(self.quit_event)
            elif self.strategy == 'IDA':
                self.IDA()

    def uniform(self):
        # print('STRATEGY::', 'Uniform Search for ', self.agent.name, file=sys.stderr, flush=True)
        self.state.reset_state()
        self.agent.reset_plan()
        self.goal_found = False

        frontier = list()
        expanded = set()
        heappush(frontier, (self.state.cost, self.state))

        while frontier and not self.goal_found:
            _, s = heappop(frontier)
            expanded.add(s)

            if not self.goal_found:
                for action in self.agent.getPossibleActions(s):
                    s_child = s.create_child(action, cost=1, ghostmode=self.ghostmode)
                    if s_child:
                        self.__is_goal__(self.agent, s_child)
                        if self.goal_found:
                            return True
                        elif ((s_child.f(), s_child) not in frontier) and not (s_child in expanded):
                            heappush(frontier, (s_child.cost, s_child))

        return False

    def bfs(self, bound=INF):
        # print('STRATEGY::', 'BFS Strategy for ', self.agent.name, file=sys.stderr, flush=True)
        if self.max_depth:
            bound = self.max_depth
        frontier = deque()
        expanded = set()
        frontier.append(self.state)

        while frontier and not self.goal_found:
            s = frontier.popleft()
            expanded.add(s)
            if not self.goal_found:
                for action in self.agent.getPossibleActions(s, ghostmode=self.ghostmode):
                    s_child = s.create_child(action, cost=1, ghostmode=self.ghostmode)
                    if s_child:
                        self.__is_goal__(self.agent, s_child, multi_goal=self.multi_goal)
                        if self.goal_found:
                            return True

                        elif (s_child not in frontier) and (s_child not in expanded):
                            if s_child.cost < bound:
                                frontier.append(s_child)

        return False

    def dfs(self, bound=INF):
        # print('STRATEGY::', 'DFS Strategy for ', self.agent.name, file=sys.stderr, flush=True)
        if self.max_depth:
            bound = self.max_depth
        frontier = list()
        expanded = set()
        frontier.append(self.state)

        while frontier and not self.goal_found:
            s = frontier.pop()
            expanded.add(s)

            if not self.goal_found:
                for action in self.agent.getPossibleActions(s):
                    s_child = s.create_child(action, cost=1, ghostmode=self.ghostmode)
                    if s_child:
                        self.__is_goal__(self.agent, s_child)
                        if self.goal_found:
                            return True

                        elif (s_child not in frontier) and (s_child not in expanded):
                            if s_child.cost < bound:
                                frontier.append(s_child)

        return False

    def best_first(self, bound=INF):
        if self.max_depth:
            bound = self.max_depth

        def evaluate_cost(new_state: 'State', bias=0.5):
            if new_state in expanded:
                s_ = set()
                s_.add(new_state)
                union = expanded.union(s_)
                old_state = union.pop()
                if (new_state.cost + bias) <= old_state.cost:
                    expanded.remove(old_state)

        # print('STRATEGY::', 'Best-First Strategy for ', self.agent.name, file=sys.stderr, flush=True)

        self.state.reset_state()
        self.agent.reset_plan()
        self.goal_found = False
        if self.heuristics == 'Distance':
            self.state.h_cost = DistanceBased.h(self.state, self.agent, metrics=self.metrics)
        elif self.heuristics == 'Dynamic':
            self.state.h_cost = DynamicHeuristics.h(self.state, self.agent, self.metrics, 0)
        elif self.heuristics == 'Tie Breaking':
            self.state.h_cost = TieBreaking.h(self.state, self.agent, metrics=self.metrics)
        else:
            raise Exception('STRATEGY::', 'Wrong Heuristics')

        frontier = list()
        expanded = set()

        heappush(frontier, (self.state.f(), self.state))

        while frontier and not self.goal_found:
            _, s = heappop(frontier)
            expanded.add(s)

            if not self.goal_found:
                for action in self.agent.getPossibleActions(s, ghostmode=self.ghostmode):
                    s_child = s.create_child(action, cost=0, ghostmode=self.ghostmode)
                    if s_child:

                        if self.heuristics == 'Distance':
                            s_child.h_cost = DistanceBased.h(s_child, self.agent, metrics=self.metrics)
                        elif self.heuristics == 'Dynamic':
                            s_child.h_cost = DynamicHeuristics.h(s_child, self.agent, metrics=self.metrics,
                                                                 expanded_len=len(expanded))
                        elif self.heuristics == 'Tie Breaking':
                            s_child.h_cost = TieBreaking.h(s_child, self.agent, metrics=self.metrics)
                        else:
                            raise Exception('STRATEGY::', 'Wrong Heuristics')

                        self.__is_goal__(self.agent, s_child)

                        # evaluate_cost(s_child)
                        if self.goal_found:
                            return True
                        elif ((s_child.f(), s_child) not in frontier) and not (s_child in expanded):
                            if len(expanded) < bound:

                                heappush(frontier, (s_child.f(), s_child))
                            else:
                                # print("Bound reached", file=sys.stderr)
                                return False

        return False

    def a_star(self, bound=INF):
        if self.max_depth:
            bound = self.max_depth

        def evaluate_cost(new_state: 'State', bias=0.5):
            if new_state in expanded:
                s_ = set()
                s_.add(new_state)
                union = expanded.union(s_)
                old_state = union.pop()
                if (new_state.cost + bias) <= old_state.cost:
                    expanded.remove(old_state)

        if self.agent.goal:
            goals = []
            if isinstance(self.agent.goal, list):
                goals = self.agent.goal
            else:
                goals = [self.agent.goal]

        self.state.reset_state()
        self.agent.reset_plan()
        self.goal_found = False
        if self.heuristics == 'Distance':
            self.state.h_cost = DistanceBased.h(self.state, self.agent, metrics=self.metrics)
        elif self.heuristics == 'Dynamic':
            self.state.h_cost = DynamicHeuristics.h(self.state, self.agent, self.metrics, 0)
        elif self.heuristics == 'Tie Breaking':
            self.state.h_cost = TieBreaking.h(self.state, self.agent, metrics=self.metrics)
        else:
            raise Exception('STRATEGY::', 'Wrong Heuristics')

        frontier = list()
        expanded = set()

        heappush(frontier, (self.state.f(), self.state))

        while frontier and not self.goal_found:
            _, s = heappop(frontier)
            expanded.add(s)
            # # print("h", file=sys.stderr)
            if not self.goal_found:
                # # print(s.last_action, file=sys.stderr)
                for action in self.agent.getPossibleActions(s, ghostmode=self.ghostmode):

                    s_child = s.create_child(action, cost=int(not self.ghostmode), ghostmode=self.ghostmode)
                    # s_child = s.create_child(action, 0, ghostmode=self.ghostmode)
                    # # print("child is", not s_child, file=sys.stderr)
                    if s_child:

                        if self.heuristics == 'Distance':
                            s_child.h_cost = DistanceBased.h(s_child, self.agent, metrics=self.metrics)
                        elif self.heuristics == 'Dynamic':
                            s_child.h_cost = DynamicHeuristics.h(s_child, self.agent, metrics=self.metrics,
                                                                 expanded_len=len(expanded))
                        elif self.heuristics == 'Tie Breaking':
                            s_child.h_cost = TieBreaking.h(s_child, self.agent, metrics=self.metrics)
                        else:
                            raise Exception('STRATEGY::', 'Wrong Heuristics')

                        self.__is_goal__(self.agent, s_child)

                        if self.goal_found:
                            return True
                        elif ((s_child.f(), s_child) not in frontier) and not (s_child in expanded):
                            if len(expanded) < bound:
                                heappush(frontier, (s_child.f(), s_child))
                            else:
                                # print("Bound reached", file=sys.stderr)
                                return False
        return False

    def IDA(self, h_function=DistanceBased):
        expanded = set()

        def search(state, limit):
            state.h_cost = h_function.h(state, self.agent, metrics=self.metrics)
            expanded.add((state, state.cost))
            if state.f() > limit:
                return state.f()

            minimum = INF
            if not self.goal_found:
                for action in self.agent.getPossibleActions(state):
                    s = state.create_child(action, cost=1, ghostmode=self.ghostmode)
                    if s:
                        self.__is_goal__(self.agent, s)
                        if self.goal_found:
                            # print('IDA', 'solution is found', file=sys.stderr)
                            return True
                        temporary = search(s, limit)
                        if temporary < minimum and (s, s.cost) not in expanded:
                            minimum = temporary
            return minimum

        ##IDA starts here
        self.state.h_cost = h_function.h(self.state, self.agent, metrics=self.metrics)
        threshold = self.state.h_cost
        while not self.goal_found:
            self.state.reset_state()
            expanded.clear()
            expanded.add((self.state, 0))
            temp = search(self.state, threshold)
            if self.goal_found:
                # print('IDA', 'solution is found', file=sys.stderr)
                return True
            elif temp == INF and not self.goal_found:
                # print('IDA', 'solution is not found', file=sys.stderr)
                return False
            threshold = temp
        # print('IDA', 'solution is not found', file=sys.stderr)
        return False

    def extract_plan(self, state: 'State'):
        if state:
            self.agent.current_plan.append(state.last_action)
            self.extract_plan(state.parent)
        else:
            self.agent.current_plan = self.agent.current_plan[:-1]
            self.agent.current_plan.reverse()

    def __is_goal__(self, agent: 'Agent', state: 'State', multi_goal=False) -> 'bool':
        if isinstance(agent.goal, list):
            multi_goal = True

        if not multi_goal:
            if agent.goal in state.atoms and not self.goal_found:
                self.extract_plan(state)
                self.goal_found = True

                return True
            return False
        else:
            is_goal = True
            for goal in agent.goal:
                # # print(state.atoms, file=sys.stderr)
                if goal not in state.atoms:
                    is_goal = False
            if is_goal:
                self.goal_found = True
                self.extract_plan(state)

            return is_goal
