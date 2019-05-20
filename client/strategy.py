from collections import deque
from numpy import inf, exp
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
        print(self.agent.goal, file=sys.stderr)
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
        print('STRATEGY::', 'Uniform Search for ', self.agent.name, file=sys.stderr, flush=True)
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
        print('STRATEGY::', 'BFS Strategy for ', self.agent.name, file=sys.stderr, flush=True)
        if self.max_depth:
            bound = self.max_depth
        frontier = deque()
        expanded = set()
        frontier.append(self.state)

        while frontier and not self.goal_found:
            s = frontier.popleft()
            expanded.add(s)

            if not self.goal_found:
                for action in self.agent.getPossibleActions(s):
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
        print('STRATEGY::', 'DFS Strategy for ', self.agent.name, file=sys.stderr, flush=True)
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

    def best_first(self):
        print('STRATEGY::', 'Best-First Search for ', self.agent.name, file=sys.stderr, flush=True)
        self.state.reset_state()
        self.agent.reset_plan()
        self.goal_found = False
        self.state.h_cost = DistanceBased.h(self.state, self.agent, metrics=self.metrics)

        frontier = list()
        expanded = set()
        heappush(frontier, (self.state.f(), self.state))

        while frontier and not self.goal_found:
            _, s = heappop(frontier)
            expanded.add(s)

            if not self.goal_found:
                for action in self.agent.getPossibleActions(s):
                    s_child = s.create_child(action, cost=0)
                    if s_child:
                        s_child.h_cost = DistanceBased.h(s_child, self.agent, metrics=self.metrics)
                        self.__is_goal__(self.agent, s_child)
                        if self.goal_found:
                            return True
                        elif ((s_child.f(), s_child) not in frontier) and not (s_child in expanded):
                            heappush(frontier, (s_child.f(), s_child))

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

        print('STRATEGY::', 'A* Strategy for ', self.agent.name, file=sys.stderr, flush=True)

        self.state.reset_state()
        self.agent.reset_plan()
        self.goal_found = False
        if self.heuristics == 'Distance':
            self.state.h_cost = DistanceBased.h(self.state, self.agent, metrics=self.metrics)
        elif self.heuristics == 'Dynamic':
            self.state.h_cost = DynamicHeuristics.h(self.state,self.agent, self.metrics, 0)
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
                    s_child = s.create_child(action, cost=1, ghostmode=self.ghostmode)
                    if s_child:

                        if self.heuristics == 'Distance':
                            s_child.h_cost = DistanceBased.h(s_child, self.agent, metrics=self.metrics)
                        elif self.heuristics == 'Dynamic':
                            s_child.h_cost = DynamicHeuristics.h(s_child, self.agent, metrics=self.metrics, expanded_len=len(expanded))
                        else:
                            raise Exception('STRATEGY::', 'Wrong Heuristics')

                        self.__is_goal__(self.agent, s_child)

                        #evaluate_cost(s_child)
                        if self.goal_found:
                            return True
                        elif ((s_child.f(), s_child) not in frontier) and not (s_child in expanded):
                            if len(expanded) < bound:
                               # print(len(expanded), file= sys.stderr)
                                heappush(frontier, (s_child.f(), s_child))
                            else:
                                return False

        return False

    def IDA(self, h_function=DistanceBased):
        print('STRATEGY::', 'IDA* Strategy for', self.heuristics, self.metrics, file=sys.stderr, flush=True)
        expanded = set()

        def search(state, limit):
            state.h_cost = h_function.h(state, self.agent, metrics=self.metrics)
            if state.f() > limit:
                return state.f()

            minimum = INF
            for action in self.agent.getPossibleActions(state):
                s = state.create_child(action, cost=1, ghostmode=self.ghostmode)
                if s:
                    self.__is_goal__(self.agent, s)
                    if self.goal_found:
                        print('IDA', 'solution is found', file=sys.stderr)
                        return True
                    temporary = search(s, limit)
                    if temporary < minimum and (s,s.cost) not in expanded:
                        minimum = temporary
                        expanded.add((s,  s.cost))
            return minimum

        ##IDA starts here
        self.state.h_cost = h_function.h(self.state, self.agent, metrics=self.metrics)
        threshold = exp(self.state.h_cost**2)
        while not self.goal_found:
            self.state.reset_state()
            temp = search(self.state, threshold)
            if self.goal_found:
                print('IDA', 'solution is found', file=sys.stderr)
                return True
            elif temp == INF and not self.goal_found:
                print('IDA', 'solution is not found', file=sys.stderr)
                return False
            threshold = temp
        print('IDA', 'solution is not found', file=sys.stderr)
        return False

    def extract_plan(self, state: 'State'):
        if state:
            # if self.agent.goal in state.atoms:
            #     self.agent.reset_plan()

            self.agent.current_plan.append(state.last_action)
            # print('STRATEGY::', 'CHOSEN IN PREVIOUS STATE', state.last_action['message'], 'goal::', self.agent.goal,
            #       file=sys.stderr)
            # for action in self.agent.getPossibleActions(state):
            #     s_child = state.create_child(action, cost=1)
            #     s_child.h_cost = DistanceBased.h(s_child, self.agent, metrics=self.metrics) + \
            #                      ActionPriority.h(s_child)
            #     print(action, s_child.__total_cost__(), DistanceBased.h(s_child, self.agent, metrics=self.metrics),
            #           file=sys.stderr)

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
                ### print('Plan found for agent : ' + str(agent.name) + ' with goal : ',
                ####     file=sys.stderr, flush=True)
                for goal in agent.goal:
                    print(goal, file=sys.stderr)

            return is_goal
