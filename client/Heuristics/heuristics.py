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


class GoalCount(Heuristic):
    def h(self, state: 'State') -> 'int':
        goal_count = len(self.goals)
        for atom in state.atoms:
            if atom in self.goals:  # there is no self.goals here right?
                goal_count -= 1
        return goal_count


def DistanceBased(state: 'State', agent: 'Agent', metrics='Real'):
    distance = 0
    if metrics == 'Manhattan':
        if agent.goal_details != {}:
            for goal in [agent.goal_details]:  ## if agent has multiple goals remove '[ ]'
                # print(goal, file=sys.stderr)
                min_distance = np.inf

                for atom in state.atoms:
                    if atom.name == 'BoxAt' and goal['letter'] == \
                            state.find_box_letter(atom.variables[0]).variables[1]:
                        coords = atom.variables[1]
                        agent_pos = state.find_agent(agent.name)
                        d = np.abs(coords[0] - goal['position'][0]) + np.abs(
                            coords[1] - goal['position'][1])
                        d += np.abs(coords[0] - agent_pos[0]) + np.abs(coords[1] - agent_pos[1])
                        if d < min_distance:
                            min_distance = d
                distance += min_distance

    elif metrics == 'Euclidean':
        if agent.goal_details != {}:
            for goal in [agent.goal_details]:  ## if agent has multiple goals remove '[ ]'
                min_distance = np.inf
                for atom in state.atoms:
                    # print(state.find_box_letter(atom.variables[0]).variables[1], file=sys.stderr)
                    if atom.name == 'BoxAt' and goal['letter'] == \
                            state.find_box_letter(atom.variables[0]).variables[1]:
                        coords = atom.variables[1]
                        agent_pos = state.find_agent(agent.name)
                        d = 0
                        d += np.sqrt(np.power(coords[0] - goal['position'][0], 2) + np.power(
                            coords[1] - goal['position'][1], 2))
                        d += np.sqrt(np.power(coords[0] - agent_pos[0], 2) + np.power(coords[1] - agent_pos[1], 2))
                        if d < min_distance:
                            min_distance = d
                distance += min_distance

    elif metrics == 'Real':
        if agent.goal_details != {}:
            for goal in [agent.goal_details]:  ## if agent has multiple goals remove '[ ]'
                min_distance = np.inf
                for atom in state.atoms:
                    if atom.name == 'BoxAt' and goal['letter'] == \
                            state.find_box_letter(atom.variables[0]).variables[1]:
                        coords = atom.variables[1]
                        agent_pos = state.find_agent(agent.name)
                        d = state.find_distance(coords, goal['position']) + state.find_distance(coords, agent_pos)
                        if d < min_distance:
                            min_distance = d
                        if coords == goal['position']:
                            min_distance = state.find_distance(coords, goal['position'])
                distance += min_distance
    return distance
