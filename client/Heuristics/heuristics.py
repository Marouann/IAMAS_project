from abc import ABCMeta, abstractmethod
import inspect
from state import *
from action import *
from agent import *
import numpy as np
from random import shuffle


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

class AdditiveHeuristics(Heuristic):
    def h(self, initial_state: 'State', agent: 'Agent', goal:'Atom', expanded, table) -> 'int':
        expanded.add(goal)
        table[str(goal)] = np.inf
        if goal in initial_state.atoms:
            table[str(goal)] = 0
        else:
            actions = self.getActions(initial_state, agent, goal)
            print("Goal", goal, file=sys.stderr)
            print("NB possible actions:", len(actions), file=sys.stderr)
            for a in actions:
                print(a[0].name + str(a[1]), file=sys.stderr)
            if actions != []:
                precond_of_action = list(map(lambda action: action[0].preconditions(*action[1])
                                                            , actions))
                def recursionCall(preconditions):
                    print("rec call", file=sys.stderr)
                    sum = 0
                    for p in preconditions:
                        if p not in initial_state.rigid_atoms and p not in expanded:
                            h = self.h(initial_state, agent, p, expanded, table)
                            # table[str(p)] = h
                            if h == np.inf:
                                return h
                            sum += h # Additive Heuristic, sum up all precond cost for one action
                        elif p not in initial_state.rigid_atoms and p in expanded:
                            print("atom already expanded", file=sys.stderr)
                            sum += table[str(p)]
                    # print("table:", str(table), file=sys.stderr)
                    return sum
                table[str(goal)] = 1 + min(list(map(lambda preconditions: recursionCall(preconditions), precond_of_action)))
        # table[str(goal)] = value
        print(table, file=sys.stderr)
        return table[str(goal)]



    def f(self, state: 'State') -> 'int':
        return self.h(state) + state.cost

    def getActions(self, state:'State', agent: 'Agent', goal): # goal must be one atom only
        possibleActions = []
        for action in [Move, Push]:
            positive_effects_function = action.positive_effects # retrieve positive effect of action
            args = inspect.getargspec(positive_effects_function)[0] # get list of argument of that function
            effects = positive_effects_function(*args)
            for effect in effects:
                if effect.name == goal.name:

                    if action.name == "Move" and effect.name=="AgentAt":
                        agt = agent.name
                        agtTo = goal.variables[1]
                        possibleAgtFrom = state.findNeighbour(agtTo)
                        for agtFrom in possibleAgtFrom:
                            possibleActions.append((action, (agt, agtFrom, agtTo)))

                    elif action.name == "Move" and effect.name=="Free":
                        agt = agent.name
                        agtFrom = goal.variables[0]
                        possibleAgtTo = state.findNeighbour(agtFrom)
                        for agtTo in possibleAgtTo:
                            possibleActions.append((action, (agt, agtFrom, agtTo)))

                    elif action.name == "Push" and effect.name=="AgentAt":
                        agt = agent.name
                        boxFrom = goal.variables[1]
                        possibleAgtFrom = state.findNeighbour(boxFrom)
                        possibleBoxes = state.findBoxes()
                        possibleBoxTo = state.findNeighbour(boxFrom) # restrict somehow for no swap between agt and box
                        color = agent.color
                        for box in possibleBoxes:
                            for boxTo in possibleBoxTo:
                                for agtFrom in possibleAgtFrom:
                                    if agtFrom != boxTo: # prevent exchange box and agent positions
                                        possibleActions.append((action, (agt, agtFrom, box[0], boxFrom, boxTo, color)))

                    elif action.name == "Push" and effect.name=="Free":
                        agt = agent.name
                        agtFrom = goal.variables[0]
                        possibleBoxFrom = state.findNeighbour(agtFrom)
                        possibleBoxes = state.findBoxes()
                        color = agent.color
                        for box in possibleBoxes:
                            for boxFrom in possibleBoxFrom:
                                possibleBoxTo = state.findNeighbour(boxFrom)
                                for boxTo in possibleBoxTo:
                                    if agtFrom != boxTo: # prevent exchange box and agent positions
                                        possibleActions.append((action, (agt, agtFrom, box[0], boxFrom, boxTo, color)))

                    elif action.name == "Push" and effect.name=="BoxAt":
                        agt = agent.name
                        box = goal.variables[0]
                        boxTo = goal.variables[1]
                        possibleBoxFrom = state.findNeighbour(boxTo)
                        color = agent.color
                        for boxFrom in possibleBoxFrom:
                            possibleAgtFrom = state.findNeighbour(boxFrom)
                            for agtFrom in possibleAgtFrom:
                                if agtFrom != boxTo: # prevent exchange box and agent positions
                                    possibleActions.append((action, (agt, agtFrom, box, boxFrom, boxTo, color)))

                    elif action.name == "Pull" and effect.name=="AgentAt":
                        agt = agent.name
                        agtTo = goal.variables[1]
                        possibleAgtFrom = state.findNeighbour(agtTo)
                        possibleBoxes = state.findBoxes()
                        color = agent.color
                        for box in possibleBoxes:
                            for agtFrom in possibleAgtFrom:
                                possibleBoxFrom = state.findNeighbour(agtFrom)
                                for boxFrom in possibleBoxFrom:
                                    if agtTo != boxFrom: # prevent exchange box and agent positions
                                        possibleActions.append((action, (agt, agtFrom, agtTo, box[0], boxFrom, color)))

                    elif action.name == "Pull" and effect.name=="Free":
                        agt = agent.name
                        boxFrom = goal.variables[0]
                        possibleAgtFrom = state.findNeighbour(boxFrom)
                        possibleBoxes = state.findBoxes()
                        color = agent.color
                        for box in possibleBoxes:
                            for agtFrom in possibleAgtFrom:
                                possibleAgtTo = state.findNeighbour(agtFrom)
                                for agtTo in possibleAgtTo:
                                    if agtTo != boxFrom: # prevent exchange box and agent positions
                                        possibleActions.append((action, (agt, agtFrom, agtTo, box[0], boxFrom, color)))

                    elif action.name == "Pull" and effect.name=="BoxAt":
                        agt = agent.name
                        box = goal.variables[0]
                        agtFrom = goal.variables[1]
                        possibleAgtTo = state.findNeighbour(agtFrom)
                        possibleBoxFrom = state.findNeighbour(agtFrom)
                        color = agent.color
                        for agtTo in possibleAgtTo:
                            for boxFrom in possibleBoxFrom:
                                if agtTo != boxFrom: # prevent exchange box and agent positions
                                    possibleActions.append((action, (agt, agtFrom, agtTo, box, boxFrom, color)))
        # shuffle(possibleActions)
        return possibleActions
    def __repr__(self):
        pass
