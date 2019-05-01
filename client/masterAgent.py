import argparse
import re
import sys
import numpy as np
#from collections import deque

from state import State
from atom import Atom
from agent import *
from action import *
from knowledgeBase import KnowledgeBase
from utils import STATUS_WAIT_REPLAN


class MasterAgent:
    def __init__(self, initial_state: 'State', agents: '[Agent]', boxes: '[dict]'):
        self.currentState = initial_state

        self.agents = []
        self.boxes = boxes  # List of { 'name': Box, 'letter': char, 'color': color }
        self.goalsInAction = []

        for agt in sorted(agents, key=lambda k: k['name']):
            agtAt = initial_state.find_agent(agt['name'])
            agent = Agent(agt['name'], agtAt, None, [Move, Push, Pull, NoOp], agt['color'])
            self.agents.append(agent)

    def assignGoals(self, agentsToReplan):
        (goalsToAssign, goalsMet) = self.currentState.get_unmet_goals()
        if agentsToReplan != []:
            print('\nFree agents : ' + str([agent.name for agent in agentsToReplan]), file=sys.stderr, flush=True)
            print('Goals unmet : ' + str(goalsToAssign), file=sys.stderr, flush=True)
            print('Goals already met : ' + str(goalsMet), file=sys.stderr, flush=True)


        boxesHandled = []
        # Boxes already placed on the goal
        for goal in goalsMet:
            boxOnGoal = self.currentState.find_box(goal['position'])
            boxesHandled.append(boxOnGoal.variables[0])

        # Boxes that are currently hadnled by agents
        for agent in self.agents:
            if agent.goal is not None:
                boxesHandled.append(agent.goal.variables[0])

        # print('Box handled:', boxesHandled, file = sys.stderr)

        # Each agent that is passed to assignGoals either finished doing its job, or it's his 1st one
        # Hence we if self.goalsInAction contains agent.goal this job has been finished so we need to remove it
        for agent in agentsToReplan:
            if agent.goal_details in self.goalsInAction:
                self.goalsInAction.remove(agent.goal_details)

        for goal in self.goalsInAction:
            if goal in goalsToAssign:
                goalsToAssign.remove(goal)

        prioritizedGoals = self.prioritizeGoals(goalsToAssign)

        if prioritizedGoals != []:
            for agent in agentsToReplan:
                if agent.current_plan != []:

                    print(agent.name, agent.current_plan[0], file=sys.stderr, flush=True)
                else:
                    print('Agent', agent.name, 'has no plan!', file=sys.stderr, flush=True)
                # print(agent.occupied, file=sys.stderr)
                if agent.occupied == False:
                    print('Agent', agent.name, 'is not occupied!', file=sys.stderr, flush=True)
                    for goal in prioritizedGoals:
                        if agent.goal is not None:
                            # print('Agent already has a goal, continue: ' + str(goal), file=sys.stderr, flush=True)
                            continue
                        if goal in self.goalsInAction:
                            # print('Goal has already been assigned : ' + str(goal), file=sys.stderr, flush=True)
                            continue
                        possibleBoxes = []
                        for box in self.boxes:
                            if box['color'] == agent.color and \
                                    box['letter'] == goal['letter'] and \
                                    box['name'] not in boxesHandled:
                                possibleBoxes.append(box)
                        # print('Possible boxes:', possibleBoxes, file=sys.stderr)

                        prioritizedBoxes = sorted (possibleBoxes,
                                                   key=lambda x: self.currentState.find_box_goal_distance(x["name"], goal))
                        goalNotAssigned = True
                        while goalNotAssigned and prioritizedBoxes != []:
                            box = prioritizedBoxes.pop(0)
                            boxAlreadyPlaced = False
                            for goalmet in goalsMet:
                                boxPlaced = self.currentState.find_box(goalmet['position'])
                                if boxPlaced.variables[0] == box['name']:
                                    boxAlreadyPlaced = True

                            if not boxAlreadyPlaced:
                                agent.assignGoal(Atom("BoxAt", box['name'], goal['position']), goal)
                                self.goalsInAction.append(goal)
                                boxesHandled.append(box['name'])
                                goalNotAssigned = False
                                if not agent.goal in self.currentState.atoms:
                                    agent.plan(self.currentState)

        for agent in agentsToReplan:
            print('agent: ' + str(agent.name) + ', has goal: ' + str(agent.goal), file=sys.stderr, flush=True)



    def solveLevel(self):
        # We need to check the goal.
        self.assignGoals(self.agents)

        previous_action = [[]]
        # Store previous and current joint actions
        for agt_index in range(len(self.agents)):
            action = {'action': NoOp, 'params': [agt_index, self.currentState.find_agent(agt_index)],
                                    'message':'NoOp',
                                    'priority':4}

            previous_action[0].append(action)    # [ pop(0) <-[Previous joint action], [Current joint action] <- append(jointaction)]

        # counter in while
        nb_iter = 0
        # stop util reached goal
        while self.currentState.get_unmet_goals()[0] != []:
            # First we loop over agent to free them if their goal are met

            self.assignGoals([agent for agent in self.agents if agent.occupied == False])
            nb_iter += 1

            # Gets the first actions from each agent (joint action on first row)
            actions_to_execute = self.getNextJointAction()

            # update previous joint action
            previous_action.append(actions_to_execute)
            previous_action.pop(0)
            # print('Previous actions : ' + str(previous_action), file=sys.stderr, flush=True)


            # Keep the response from the server ([true, false, ...])
            valid = self.executeAction(actions_to_execute)
            print('Server response : ' + str(valid), file=sys.stderr, flush=True)

            # 'agents_with_conflit': List of agents which cannot execute their actions (e.g [agt0, agt1, agt6])
            agents_with_conflit = [i for i in range(len(valid)) if valid[i]=='false']

            # If 'agents_with_conflit' not empty then solve conflict
            if agents_with_conflit != []:
                self.solveConflict(agents_with_conflit,actions_to_execute, previous_action)

            # Replan for agents that have goals but no plan (i.e. status "W")
            for agent in self.agents:
                if agent.status == STATUS_WAIT_REPLAN:
                    agent.plan(self.currentState)
                    if agent.current_plan != []:
                        agent.status = None


    def getNextJointAction(self):
        # initialize joint_action with 'NoOp' of length number of agents ['NoOp', 'NoOp', 'NoOp', ...]
        joint_action = []
        for agent in self.agents:
            # If there are still actions in current plan pop the first action and
            if agent.current_plan != []:
                joint_action.append(agent.current_plan.pop(0))
            else:
                joint_action.append({'action': NoOp,
                                            'params': [agent.name, self.currentState.find_agent(agent.name)],
                                            'message':'NoOp',
                                            'priority':4})

        return joint_action

    def prioritizeGoals(self, goals):
        # Sort goals 1st by number of free neighbour fields, then by number of neighbour goals)
        sortedGoals = sorted(goals,
                                key=lambda x: (self.currentState.getNeithbourFieldsWithoutGoals(x["position"]).__len__(),
                                self.currentState.getNeithbourGoals(x["position"]).__len__()))

        return sortedGoals

    def solveConflict(self, agents_with_conflit, actions, previous_action):
        print('\n************* Solve conflict ***************************************\n', file=sys.stderr, flush=True)
        # print('actions : ' + str(actions), file=sys.stderr, flush=True)

        # Return list of conflicting agents
        conflicting_agents = self.getConflictingAgents(agents_with_conflit, actions, previous_action)

        print('\nFINAL OUTPUT conflicting_agents : ' + str(conflicting_agents), file=sys.stderr, flush=True)

        print('\n*********************************************************************\n', file=sys.stderr, flush=True)

        # Set a priority agent (in this cases the first one in the array)

        # Remove vice-versa conflicts
        conflicting_agents = self.removeViceVersaConflicts(conflicting_agents)

        print('\nRemoving vice-versa conflicts : ' + str(conflicting_agents), file=sys.stderr, flush=True)

        for conflict in conflicting_agents:
            # Prioritize first agent:  [1st agent, 2nd agent]
            priority_agent = conflict[0]   # 1st agent in conflict
            conflict_solver = conflict[1]   # 2nd agent in conflict

            action_of_priority_agent = actions[priority_agent]
            preconditions = action_of_priority_agent['action'].preconditions(*action_of_priority_agent['params'])

            unmet_preconditions = []
            for atom in preconditions:
                if atom not in self.currentState.atoms and atom not in self.currentState.rigid_atoms:
                    unmet_preconditions.append(atom)
            print("preconditions", unmet_preconditions, file=sys.stderr)
            if unmet_preconditions != []:
                keep_goal = self.agents[conflict_solver].goal
                keep_goal_details = self.agents[conflict_solver].goal_details
                self.agents[conflict_solver].assignGoal(unmet_preconditions[0], {})
                self.agents[conflict_solver].current_plan = []
                self.agents[conflict_solver].plan(self.currentState)
                # self.agents[conflict_solver].plan(self.currentState, strategy='best-first')

                # actionsToResolveConflicts = [NoOp for i in range(len(self.agents))]
                actionsToResolveConflicts = [{'action': NoOp,
                                            'params': [i, self.currentState.find_agent(i)],
                                            'message':'NoOp',
                                            'priority':4} for i in range(len(self.agents))]

                actionsToResolveConflicts[conflict_solver] = self.agents[conflict_solver].current_plan[0]
                self.executeAction(actionsToResolveConflicts)  # generalize this for more than 2 agents conflicting

                # self.agents[conflict_solver].assignGoal(keep_goal)
                print(keep_goal, keep_goal_details, file=sys.stderr)
                self.agents[conflict_solver].assignGoal(keep_goal, keep_goal_details)
                self.agents[conflict_solver].status = STATUS_WAIT_REPLAN


                self.agents[priority_agent].current_plan = [action_of_priority_agent] + self.agents[
                    priority_agent].current_plan

            else:
                # actionsToResolveConflicts = ['NoOp' for i in range(len(self.agents))]
                actionsToResolveConflicts = [{'action': NoOp,
                                            'params': [i, self.currentState.find_agent(i)],
                                            'message':'NoOp',
                                            'priority':4} for i in range(len(self.agents))]
                actionsToResolveConflicts[priority_agent] = action_of_priority_agent

                self.executeAction(actionsToResolveConflicts)  # generalize this for more than 2 agents conflicting


    '''
    Remove vice-versa conflicts:
    - initial list: [[0, 1], [1, 0], [2, 3],[3, 2]]
    - remove: [1, 0] and [3, 2]
    - final list: [[0, 1], [2, 3]]
    '''
    def removeViceVersaConflicts(self, conflicting_agents):
        for x in conflicting_agents:
                for y in conflicting_agents:
                    # if sets are equal and not same set
                    if set(x) == set(y) and x != y:
                        conflicting_agents.remove(y)

        return conflicting_agents

    '''
    Return's "conflicting_agents": which is a list containing pairs of agents:

    "[[0, x], [1, x], [2, x],...,[n, x]]"

    A pair of agents: [A, B] (precondition of agent A is conflicts with negative effect of B)

    '''
    def getConflictingAgents(self, agents_with_conflit, actions, previous_action):

        conflicting_agents = []
        # goes through agents with a conflit
        for current_agent in agents_with_conflit:

            # get preconditions
            action_of_current_agent = actions[current_agent]
            preconditions_of_current_agent = action_of_current_agent['action'].preconditions(*action_of_current_agent['params'])
            # get unmet_preconditions
            unmet_preconditions = []
            for atom in preconditions_of_current_agent:
                print(atom, file=sys.stderr)
                print(self.currentState.atoms, file=sys.stderr)
                if atom not in self.currentState.atoms and atom not in self.currentState.rigid_atoms:
                    unmet_preconditions.append(atom)


            for agent in self.agents:
                # This is to not repeat the current agent (agent cannot conflict with himslef).
                if int(agent.name) != current_agent:

                    # get agent's previous action
                    # print(previous_action, file=sys.stderr)
                    prev_action_of_agent = previous_action[0][int(agent.name)]

                    negative_effects_of_agent = prev_action_of_agent['action'].negative_effects(*prev_action_of_agent['params'])



                    print('\nagent[' + str(current_agent) + '] unmet pre. : ', file=sys.stderr, flush=True)
                    for i in range(len(unmet_preconditions)):
                        print(str(unmet_preconditions[i]), file=sys.stderr, flush=True)

                    for atoms in unmet_preconditions:
                        if atoms in negative_effects_of_agent:
                            agent_in_conlfict = int(agent.name)
                            conflicting_agents.append([current_agent, agent_in_conlfict])

                            print('\nCONFLICT', file=sys.stderr, flush=True)
                            print('\nAgent in conflict : ' + str(agent_in_conlfict), file=sys.stderr, flush=True)
                            print('\nconflicting_agents : ' + str(conflicting_agents), file=sys.stderr, flush=True)
                            print('\n+++++++++++++++++++++++++++', file=sys.stderr, flush=True)

                        # just for the sake of the print statement (should be removed)
                        elif atoms not in negative_effects_of_agent:
                            print('\nNO CONFLICT', file=sys.stderr, flush=True)
                            print('\n+++++++++++++++++++++++++++', file=sys.stderr, flush=True)

        return conflicting_agents


    '''
    actionList is a 2D array of actions (size number_action_to_execute * number_of_agents).
        - a row corresponds to a joint action
        - each col represents action of a specific agent

    return successive result of the server to actions, same size as input
    '''

    def executeAction(self, jointAction):
        # print('I am executing actions', file=sys.stderr, flush=True)

        server_answer = ''
        actions_string = ''
        # print(jointAction, file=sys.stderr, flush=True)
        for agent_action in jointAction:

            actions_string += agent_action['message']
            actions_string += ';'

        actions_string = actions_string[:-1]  # remove last ';' from the string

        # retrieve answer from server and separate answer for specific action
        # [:-1] is only to remove the '\n' at the end of response
        print(actions_string, file=sys.stderr, flush=True)  # print out
        print(actions_string, flush=True)  # send to server

        server_answer = sys.stdin.readline()[:-1].split(";")

        for i, answer in enumerate(server_answer):
            if answer == 'true':
                #if jointAction[i]['action'].name != 'NoOp':

                jointAction[i]['action'].execute(self.currentState, jointAction[i]['params'])

        for agent in self.agents:
            if agent.goal in self.currentState.atoms:
                agent.occupied = False
                agent.current_plan = []
                agent.goal = None

        return server_answer
