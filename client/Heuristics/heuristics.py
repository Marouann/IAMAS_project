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
    def h(state: 'State', agent: 'Agent', metrics, expanded_len = None, scaler=1.0) -> 'float':
        distance = 0.0
        agent_pos = state.find_agent(agent.name)
        if agent.goal:
            for goal in [agent.goal]:
                min_distance = MAX_DISTANCE
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
        return distance

    @staticmethod
    def f(state: 'State', agent: 'Agent', metrics='Real') -> 'float':
        return state.cost + DistanceBased.h(state, agent, metrics)


class ConnectionHeuristics(Heuristic):
    pass


class DynamicHeuristics(Heuristic):
    @staticmethod
    def h(state: 'State', agent: 'Agent', metrics,
           expanded_len,
          goal_scaler=50., distance_scaler=10.0) -> 'float':

        weight = math.exp(-expanded_len/len(state))
        h = DistanceBased.h(state, agent, metrics, weight * distance_scaler) + weight * GoalCount.h(state, goal_scaler)
        print(math.log100((expanded_len+1)), file=sys.stderr)
        return h
    @staticmethod
    def evaluate_state(state:'State'):
        pass

    @staticmethod
    def f(state: 'State', agent: 'Agent', metrics='Real') -> 'float':
        return state.cost + DynamicHeuristics.h(state, agent, metrics, expanded_len=0)
