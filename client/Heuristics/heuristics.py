from abc import ABCMeta, abstractmethod
import inspect
from state import *
from action import *
from agent import *
import numpy as np


class Heuristic(metaclass=ABCMeta):
    def __init__(self, initial_state: 'State', goals: 'KnowledgeBase'):
        self.goals = goals
        self.initial_state = initial_state

    @abstractmethod
    def h(self, state: 'State') -> 'int': raise NotImplementedError

    @abstractmethod
    def f(self, state: 'State') -> 'int': raise NotImplementedError

    @abstractmethod
    def __repr__(self):
        pass


class GoalCount(Heuristic):
    def h(self, state: 'State') -> 'int':
        goal_count = len(self.goals)
        for atom in state.atoms:
            if atom in self.goals:  # there is no self.goals here right?
                goal_count -= 1
        return goal_count

    def f(self, state: 'State') -> 'int':
        return self.h(state) + state.cost

    def __repr__(self):
        pass


class DistanceBased(Heuristic):
    # def h(self, state: 'State', metrics='Manhattan'):
    #     distance = 0
    #     if metrics == 'Manhattan':
    #         for atom in state.atoms:
    #             if atom.name == 'BoxAt':
    #                 coords = atom.variables[1]
    #                 distance_min = np.inf
    #                 for goal in state.goals:
    #                     distance_current = np.abs(coords[0] - goal['position'][0]) + np.abs(
    #                         coords[1] - goal['position'][1])
    #                     if distance_current < distance_min:
    #                         distance_min = distance_current
    #                 distance += distance_min
    def h(self, state: 'State', agent:'Agent', metrics='Manhattan'):
        distance = 0
        if metrics == 'Manhattan':
            if agent.goal_details != {}:
                for goal in [agent.goal_details]: ## if agent has multiple goals remove '[ ]'
                    # print(goal, file=sys.stderr)
                    min_distance = np.inf
                    for atom in state.atoms:
                        # print(state.findBoxLetter(atom.variables[0]).variables[1], file=sys.stderr)
                        if atom.name == 'BoxAt' and  goal['letter']== state.findBoxLetter(atom.variables[0]).variables[1]:
                            coords = atom.variables[1]
                            agent_pos = state.findAgent(agent.name)
                            d = 0
                            d += np.abs(coords[0] - goal['position'][0]) + np.abs(
                                coords[1] - goal['position'][1])
                            d += np.abs(coords[0] - agent_pos[0]) + np.abs(coords[1] - agent_pos[1])
                            if d < min_distance:
                                min_distance = d
                    distance += min_distance




        elif metrics=='Euclidean':
            for atom in state.atoms:
                if atom.name == 'BoxAt':
                    coords = atom.variables[1]
                    distance_min = np.inf
                    for goal in state.goals:
                        distance_current = np.sqrt(np.power(coords[0] - goal['position'][0],2) + np.power(
                            coords[1] - goal['position'][1],2))
                        if distance_current < distance_min:
                            distance_min = distance_current

                    distance += distance_min
        return distance

    def f(self, state: 'State'):
        pass

    def __repr__(self):
        pass

# class AdditiveHeuristics(Heuristic):
#     def h(self, state: 'State') -> 'int':
#         goal_count = self.goals.len()
#         for atom in state.atoms:
#             if atom in self.goals: # there is no self.goals here right?
#                 goal_count -= 1
#         return goal_count
#
#     def f(self, state: 'State') -> 'int':
#         return self.h(state) + state.cost
#
#     def getActions(self, state:'State', goal, agent: 'Agent'): # goal must be one atom only
#         possibleActions = []
#         for action in [Move, Push, Pull]:
#             positive_effects_function = action[1] # retrieve positive effect of action
#             args = inspect.getargspec(positive_effects_function)[0] # get list of argument of that function
#             effects = positive_effects_function(*args)
#             for effect in effects:
#                 if action.name == "Move" and effect.name="AgentAt":
#                     agt = agent.agt
#                     agtFrom = effect.variables[1]
#                     possibleAgtTo = findNeighbour(agtFrom)
#                     for agtTo in possibleAgtTo:
#                         possibleActions.append(action, (agt, agtFrom, agtTo))
#
#                 elif action.name == "Move" and effect.name="Free":
#                     agt = agent.agt
#                     agtTo = effect.variables[0]
#                     possibleAgtFrom = findNeighbour(agtTo)
#                     for agtFrom in possibleAgtFrom:
#                         possibleActions.append(action, (agt, agtFrom, agtTo))
#
#                 elif action.name == "Push" and effect.name="AgentAt":
#                     agt = agent.agt
#                     boxFrom = effect.variables[1]
#                     possibleAgtFrom = findNeighbour(boxFrom)
#                     box = state.findBox(boxFrom)
#                     possibleBoxTo = findNeighbour(boxFrom) # restrict somehow for no swap between agt and box
#                     color = agent.color
#                     for boxTo in possibleBoxTo:
#                         for agtFrom in possibleAgtFrom
#                             possibleActions.append(action, (agt, agtFrom, box, boxFrom, boxTo, color))
#
#                 elif action.name == "Push" and effect.name="Free":
#                     agt = agent.agt
#                     agtFrom = effect.variables[0]
#                     possibleBoxFrom = findNeighbour(agtFrom)
#                     box = state.findBox(boxFrom)
#                     possibleBoxTo = findNeighbour(boxFrom)
#                     color = agent.color
#                     for boxFrom in possibleBoxFrom:
#                         for boxTo in possibleBoxTo:
#                             possibleActions.append(action, (agt, agtFrom, box, boxFrom, boxTo, color))
#
#                 elif action.name == "Push" and effect.name="BoxAt":
#                     agt = agent.agt
#                     box = effect.variables[0]
#                     boxTo = effect.variables[1]
#                     possibleBoxFrom = findNeighbour(boxTo)
#                     possibleAgtFrom = findNeighbour(boxFrom)
#                     color = agent.color
#                     for boxFrom in possibleBoxFrom:
#                         for agtFrom in possibleAgtFrom:
#                             possibleActions.append(action, (agt, agtFrom, box, boxFrom, boxTo, color))
#
#                 elif action.name == "Pull" and effect.name="AgentAt":
#                     agt = agent.agt
#                     agtTo = effect.variables[1]
#                     possibleAgtFrom = findNeighbour(agtTo)
#                     possibleBoxFrom = findNeighbour(agtFrom)
#                     box = state.findBox(boxFrom)
#                     color = agent.color
#                     for agtFrom in possibleAgtFrom:
#                         for boxFrom in possibleBoxFrom:
#                             possibleActions.append(action, (agt, agtFrom, agtTo, box, boxFrom, color))
#
#                 elif action.name == "Pull" and effect.name="Free":
#                     agt = agent.agt
#                     boxFrom = effect.variables[0]
#                     possibleAgtFrom = findNeighbour(boxFrom)
#                     possibleAgtTo = findNeighbour(agtFrom)
#                     box = state.findBox(boxFrom)
#                     color = agent.color
#                     for agtFrom in possibleAgtFrom:
#                         for agtTo in possibleAgtTo:
#                             possibleActions.append(action, (agt, agtFrom, agtTo, box, boxFrom, color))
#
#                 elif action.name == "Pull" and effect.name="BoxAt":
#                     agt = agent.agt
#                     box = effect.variables[0]
#                     agtFrom = effect.variables[1]
#                     possibleAgtTo = findNeighbour(agtFrom)
#                     possibleBoxFrom = findNeighbour(agtFrom)
#                     color = agent.color
#                     for agtTo in possibleAgtTo:
#                         for boxFrom in possibleBoxFrom:
#                             possibleActions.append(action, (agt, agtFrom, agtTo, box, boxFrom, color))
