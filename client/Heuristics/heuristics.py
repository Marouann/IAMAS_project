from abc import ABCMeta, abstractmethod
import inspect
from state import *
from action import *


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
            if atom in self.goals: # there is no self.goals here right?
                goal_count -= 1
        return goal_count

    def f(self, state: 'State') -> 'int':
        return self.h(state) + state.cost

class AdditiveHeuristics(Heuristic):
    def h(self, state: 'State') -> 'int':
        goal_count = self.goals.len()
        for atom in state.atoms:
            if atom in self.goals: # there is no self.goals here right?
                goal_count -= 1
        return goal_count

    def f(self, state: 'State') -> 'int':
        return self.h(state) + state.cost

    def getActions(self, state, goal, agent): # goal must be one atom only
        possibleActions = []
        for action in [Move, Push, Pull]:
            positive_effects_function = action[1] # retrieve positive effect of action
            args = inspect.getargspec(positive_effects_function)[0] # get list of argument of that function
            effects = positive_effects_function(*args)
            for effect in effects:
                if action.name == "Move" and effect.name="AgentAt":
                    agt = agent.agt
                    agtFrom = effect.variables[1]
                    agtTo = findNeighbour(agtFrom)
                    possibleActions.append(action, (agt, agtFrom, agtTo))

                elif action.name == "Move" and effect.name="Free":
                    agt = agent.agt
                    agtTo = effect.variables[0]
                    agtFrom = findNeighbour(agtTo)
                    possibleActions.append(action, (agt, agtFrom, agtTo))

                elif action.name == "Push" and effect.name="AgentAt":
                    agt = agent.agt
                    boxFrom = effect.variables[1]
                    agtFrom = findNeighbour(boxFrom)
                    box = state.findBox(boxFrom)
                    boxTo = findNeighbour(boxFrom) # restrict somehow for no swap between agt and box
                    color = agent.color
                    possibleActions.append(action, (agt, agtFrom, box, boxFrom, boxTo, color))

                elif action.name == "Push" and effect.name="Free":
                    agt = agent.agt
                    agtFrom = effect.variables[0]
                    boxFrom = findNeighbour(agtFrom)
                    box = state.findBox(boxFrom)
                    boxTo = findNeighbour(boxFrom)
                    color = agent.color
                    possibleActions.append(action, (agt, agtFrom, box, boxFrom, boxTo, color))

                elif action.name == "Push" and effect.name="BoxAt":
                    agt = agent.agt
                    box = effect.variables[0]
                    boxTo = effect.variables[1]
                    boxFrom = findNeighbour(boxTo)
                    agtFrom = findNeighbour(boxFrom)
                    color = agent.color
                    possibleActions.append(action, (agt, agtFrom, box, boxFrom, boxTo, color))

                elif action.name == "Pull" and effect.name="AgentAt":
                    agt = agent.agt
                    agtTo = effect.variables[1]
                    agtFrom = findNeighbour(agtTo)
                    boxFrom = findNeighbour(agtFrom)
                    box = state.findBox(boxFrom)
                    color = agent.color
                    possibleActions.append(action, (agt, agtFrom, agtTo, box, boxFrom, color))

                elif action.name == "Pull" and effect.name="Free":
                    agt = agent.agt
                    boxFrom = effect.variables[0]
                    agtFrom = findNeighbour(boxFrom)
                    agtTo = findNeighbour(agtFrom)
                    box = state.findBox(boxFrom)
                    color = agent.color
                    possibleActions.append(action, (agt, agtFrom, agtTo, box, boxFrom, color))

                elif action.name == "Pull" and effect.name="BoxAt":
                    agt = agent.agt
                    box = effect.variables[0]
                    agtFrom = effect.variables[1]
                    agtTo = findNeighbour(agtFrom)
                    boxFrom = findNeighbour(agtFrom)
                    color = agent.color
                    possibleActions.append(action, (agt, agtFrom, agtTo, box, boxFrom, color))
