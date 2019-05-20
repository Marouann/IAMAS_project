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
            goals = []
            if isinstance(agent.goal, list):
                goals = agent.goal
            else:
                goals = [agent.goal]

            for goal in goals:
                min_distance = MAX_DISTANCE


                if goal.name == 'Free':
                    goal_pos = goal.variables[0]
                    if metrics == 'Manhattan':
                        d = manhattan(agent_pos, goal_pos)
                    elif metrics == 'Euclidean':
                        d = euclidean(agent_pos, goal_pos)
                    else:  # real metrics
                        d = state.find_distance(agent_pos, goal_pos)
                    if d < min_distance:
                        min_distance = d
                    distance += min_distance
                else:
                    goal_pos = goal.variables[1]
                    matching_boxes = state.return_matching_boxes(goal.variables[0])
                    for box in matching_boxes:
                        atom = StaticAtom('BoxAt^', box)
                        if atom in state.atoms:
                            pos = state.atoms[atom].property()
                            if metrics == 'Manhattan':
                                d = manhattan(pos,goal_pos) + manhattan(pos, agent_pos)
                            elif metrics == 'Euclidean':
                                d = euclidean(pos, goal_pos) + euclidean(pos, agent_pos)
                            else:  # real metrics
                                d = state.find_distance(pos, goal_pos) #+ \
                                   # state.find_distance(pos, agent_pos)
                            if d < min_distance:
                                min_distance = d
                        distance += min_distance
        return float(distance)


class ConnectionHeuristics(Heuristic):
    pass

class DynamicHeuristics(Heuristic):
    @staticmethod
    def h(state: 'State', agent: 'Agent', metrics, expanded_len,
          goal_scaler=25., distance_scaler=5.0) -> 'float':

        weight = math.exp(-expanded_len/len(state.atoms))

        h = DistanceBased.h(state, agent, metrics, distance_scaler, distance_scaler) + GoalCount.h(state, goal_scaler)
        return h
