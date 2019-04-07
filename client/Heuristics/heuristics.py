from abc import ABCMeta, abstractmethod
from state import *


class Heuristic(metaclass=ABCMeta):
    def __init__(self, initial_state: 'State', goals: 'KnowledgeBase'):
        self.goals = goals
        self.initial_state = initial_state

    @abstractmethod
    def h(self, state: 'State') -> 'int': raise NotImplementedError

    @abstractmethod
    def f(self, state: 'State') -> 'int': raise NotImplementedError

    @abstractmethod
    def __repr__(self): raise NotImplementedError


class GoalCount(Heuristic):
    def h(self, state: 'State') -> 'int':
        goal_count = self.goals.len()
        for atom in state.atoms:
            if atom in self.goals:
                goal_count -= 1
        return goal_count

    def f(self, state: 'State') -> 'int':
        return self.h(state) + state.cost

class AdditiveHeuristics(Heuristic):
    pass


