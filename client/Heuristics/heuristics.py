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




class ActionPriority(Heuristic):
    @staticmethod
    def h(state: 'State', scaler=1.0) -> 'float':
        return state.last_action['priority'] * scaler




class DistanceBased(Heuristic):
    @staticmethod
    def h(state: 'State', agent: 'Agent', metrics, expanded_len = None, scaler= 1.0, scaler_2 = 1.0) -> 'float':
        distance = 0.0
        agent_pos = state.find_agent(agent.name)
        if agent.goal:
            for goal in [agent.goal]:
                min_distance = MAX_DISTANCE
                atom = StaticAtom('BoxAt^', goal.variables[0])
                if atom in state.atoms:
                    pos = state.atoms[atom].property()
                    if metrics == 'Manhattan':
                        d = manhattan(pos, goal.variables[1]) + manhattan(pos, agent_pos)
                    elif metrics == 'Euclidean':
                        d = euclidean(pos, goal.variables[1]) + euclidean(pos, agent_pos)
                    else:  # real metrics
                        d = state.find_distance(pos, goal.variables[1]) + \
                             state.find_distance(pos, agent_pos)
                    if d < min_distance:
                        min_distance = d
                distance += min_distance
        return distance



class ConnectionHeuristics(Heuristic):
    pass


class DynamicHeuristics(Heuristic):
    @staticmethod
    def h(state: 'State', agent: 'Agent', metrics, expanded_len,
          goal_scaler=25., distance_scaler=5.0) -> 'float':

        weight = math.exp(-expanded_len/10000)
        weight = 1

        h = DistanceBased.h(state, agent, metrics, distance_scaler, weight * distance_scaler) + \
            weight * GoalCount.h(state, goal_scaler)
        return h
