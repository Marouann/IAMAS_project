from Heuristics.distance import manhattan, euclidean
from state import *

MAX_DISTANCE = 1000


class Heuristic:
    pass


class GoalCount(Heuristic):
    @staticmethod
    def h(state: 'State', scaler=5.0) -> 'float':
        goal_count = len(state.get_unmet_goals()[0])
        return goal_count * scaler

    @staticmethod
    def f(state: 'State', scaler=1.0) -> 'float':
        return state.cost + GoalCount.h(state, scaler=scaler)


class ActionPriority(Heuristic):
    @staticmethod
    def h(state: 'State', scaler=1.0) -> 'float':
        return state.last_action['priority'] * scaler

    @staticmethod
    def f(state: 'State', scaler=1.0) -> 'float':
        return state.cost + ActionPriority.h(state, scaler=scaler)


class DistanceBased(Heuristic):
    @staticmethod
    def h(state: 'State', agent: 'Agent', metrics, scaler = 1.0) -> 'float':
        distance = 0
        agent_pos = state.find_agent(agent.name)
        if agent.goal:
            goals = []
            if isinstance(agent.goal, list,):
                goals = agent.goal
            else:
                goals = [agent.goal]

            for goal in goals:
                min_distance = MAX_DISTANCE
                if goal.name == 'Free':
                    if metrics == 'Manhattan':
                        d = manhattan(agent_pos, goal.variables[0])
                    elif metrics == 'Euclidean':
                        d = euclidean(agent_pos, goal.variables[0])
                    else:  # real metrics
                        d = scaler * state.find_distance(agent_pos, goal.variables[0])
                    if d < min_distance:
                        min_distance = d
                    distance += min_distance
                else:
                    for atom in state.atoms:

                        if atom.name == 'BoxAt' == goal.name and atom.variables[0] == goal.variables[0]:
                            if metrics == 'Manhattan':
                                d = manhattan(atom.variables[1], goal.variables[1]) + manhattan(atom.variables[1],
                                                                                                agent_pos)
                            elif metrics == 'Euclidean':
                                d = euclidean(atom.variables[1], goal.variables[1]) + euclidean(atom.variables[1],
                                                                                                agent_pos)
                            else:  # real metrics

                                d = scaler * state.find_distance(atom.variables[1], goal.variables[1]) + \
                                    state.find_distance(agent_pos, atom.variables[1])
                            if d < min_distance:
                                min_distance = d


                    distance += min_distance
        return float(distance)

    @staticmethod
    def f(state: 'State', agent: 'Agent', metrics='Real') -> 'float':
        return state.cost + DistanceBased.h(state, agent, metrics)

class ConnectionHeuristics(Heuristic):
    pass

class DynamicHeuristics(Heuristic):
    @staticmethod
    def h(state: 'State', agent: 'Agent', metrics,
          action_scaler=1, goal_scaler=100., decay= 1000,
          distance_scaler = 1) -> 'float':

        weight = math.exp((-state.cost)/decay)
        h = DistanceBased.h(state, agent, metrics, distance_scaler) + weight * ActionPriority.h(state, action_scaler) + \
            weight * GoalCount.h(state,  goal_scaler)
        return h

    @staticmethod
    def f(state: 'State', agent: 'Agent', metrics='Real') -> 'float':
        return state.cost + DynamicHeuristics.h(state, agent, metrics)
