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

    def prioritizeGoals(self, goals):
        # Sort goals 1st by number of free neighbour fields, then by number of neighbour goals)
        sortedGoals = sorted(goals,
                                key=lambda x: (self.currentState.getNeithbourFieldsWithoutGoals(x["position"]).__len__(),
                                self.currentState.getNeithbourGoals(x["position"]).__len__()))

        return sortedGoals

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

        # Store previous and current joint actions
        previous_action = [[]]
        for agt_index in range(len(self.agents)):
            action = {'action': NoOp, 'params': [str(agt_index), self.currentState.find_agent(str(agt_index))],
                                    'message':'NoOp',
                                    'priority':4}

            previous_action[0].append(action)    # [ pop(0) <-[Previous joint action], [Current joint action] <- append(jointaction)]

        # counter in while
        nb_iter = 0
        # stop util reached goal
        while self.currentState.get_unmet_goals()[0] != []:
            print(self.currentState.get_unmet_goals()[0], file=sys.stderr)
            nb_iter += 1
            # First we loop over agent to free them if their goal are met
            self.assignGoals([agent for agent in self.agents if agent.occupied == False])

            # Gets the first actions from each agent (joint action on first row)
            actions_to_execute = self.getNextJointAction()

            # update previous joint action
            previous_action.append(actions_to_execute)
            previous_action.pop(0)

            # Keep the response from the server ([true, false, ...])
            valid = self.executeAction(actions_to_execute)
            print('Server response : ' + str(valid), file=sys.stderr, flush=True)

            # 'agents_with_conflit': List of agents which cannot execute their actions (e.g [agt0, agt1, agt6])
            agents_with_conflit = [i for i in range(len(valid)) if valid[i]=='false']

            # If 'agents_with_conflit' not empty then solve conflict
            if agents_with_conflit != []:
                self.solveConflict(agents_with_conflit, actions_to_execute)
                # self.solveConflict(agents_with_conflit,actions_to_execute, previous_action)

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
                print(agent.current_plan, file=sys.stderr)
                joint_action.append(agent.current_plan.pop(0))
            else:
                joint_action.append({'action': NoOp,
                                            'params': [agent.name, self.currentState.find_agent(agent.name)],
                                            'message':'NoOp',
                                            'priority':4})

        return joint_action

    def executeAction(self, jointAction):
        server_answer = ''
        actions_string = ''

        for agent_action in jointAction:
            actions_string += agent_action['message']
            actions_string += ';'

        actions_string = actions_string[:-1]  # remove last ';' from the string
        print(actions_string, file=sys.stderr, flush=True)  # print out

        # retrieve answer from server and separate answer for specific action
        # [:-1] is only to remove the '\n' at the end of response
        print(actions_string, flush=True)  # send to server
        server_answer = sys.stdin.readline()[:-1].split(";")

        for i, answer in enumerate(server_answer):
            if answer == 'true':
                jointAction[i]['action'].execute(self.currentState, jointAction[i]['params'])

        for agent in self.agents:
            if agent.goal in self.currentState.atoms:
                agent.occupied = False
                agent.current_plan = []
                agent.goal = None

        return server_answer

    def solveConflict(self, agents_with_conflict, last_actions_sent):
        remaining_agents_with_conflict = list(agents_with_conflict)
        # First we check if now the action is applicable:
        # Conflict type 1.
        for i in agents_with_conflict:
            action = last_actions_sent[i]
            if action['action'].checkPreconditions(self.currentState, action['params']):
                # if the action is applicable, we apply it while stopping the others agents.
                jointAction = [{'action': NoOp, 'params': [str(agt_index), self.currentState.find_agent(str(agt_index))],
                                    'message':'NoOp',
                                    'priority':4} for agt_index in range(len(self.agents))]
                jointAction[i] = action
                remaining_agents_with_conflict.remove(i)
                self.executeAction(jointAction)

        who_is_conflicting_with = {}
        for current_agent_index in remaining_agents_with_conflict:
            who_is_conflicting_with[current_agent_index] = []
            # If the agent can not apply its action there is two case possible:
            # - The agent is conflicting alone, he wants to go on an occupied cell. But the "blocker" can continue its way without conflicting
            #       => We can make the agent wait or ask for help if the blocker does not plan to move.
            # - Two agents are trying to go on the same way
            #       => We need to prioritize someone.

            # First we need to know what is blocking
            # To do so, we need to check the unmet preconditions
            action = last_actions_sent[current_agent_index]
            preconds = action['action'].preconditions(*action['params'])
            unmet_preconds = []
            for atom in preconds:
                if atom not in self.currentState.atoms and atom not in self.currentState.rigid_atoms:
                    unmet_preconds.append(atom)

            # Now we want to know which agent has unmet this precondition
            for other_agent in [agt for agt in self.agents if int(agt.name) != current_agent_index]:
                other_agent_index = int(other_agent.name)
                # We check if the other_agent was able to performs its action
                if other_agent_index in remaining_agents_with_conflict:
                    print('two conflicting agents', file=sys.stderr)
                else:
                    other_action = last_actions_sent[other_agent_index]
                    neg_effects = other_action['action'].negative_effects(*other_action['params'])

                    other_agent_is_the_problem = False
                    for atom in unmet_preconds:
                        if atom in neg_effects:
                            other_agent_is_the_problem = True
                    
                    # If the agent is the problem, we have to store that it is conflicting with current_agent_index
                    if other_agent_is_the_problem:
                        if other_action['message'] != 'NoOp':
                            who_is_conflicting_with[current_agent_index].append({
                                'agent': other_agent_index,
                                'status': 'moving',
                                'success': True,
                            })
                        else:
                            who_is_conflicting_with[current_agent_index].append({
                                'agent': other_agent_index,
                                'status': 'waiting',
                                'success': True,
                            })
            
            # Now we know, who is conflicting, and what are they doing.
            # We can resolve the conflict
            conflicting_agents = who_is_conflicting_with[current_agent_index]
            # First, if there is only one agent that is conflicting:
            if len(conflicting_agents) == 1:
                conflicting_agent = conflicting_agents[0]
                # We check if we're in the case where the blocking agent can continue his plan
                if conflicting_agent['success']:
                    # If this agent is successful and moving we will wait.
                    # Conflict Type 2
                    if conflicting_agent['status'] == 'moving':
                        self.agents[current_agent_index].current_plan.insert(0, last_actions_sent[current_agent_index])
                        self.agents[current_agent_index].current_plan.insert(0, {
                            'action': NoOp,
                            'params': [str(current_agent_index), self.currentState.find_agent(str(current_agent_index))],
                            'message':'NoOp',
                            'priority':4,
                        })
                    # If the agent is not moving, we free the agent to let him plan for a new goal
                    # Conflit type 3
                    else:
                        self.agents[current_agent_index].status = STATUS_WAIT_REPLAN # We could free him totally.
                else:
                    # WIP
                    # Case where two agent want to go or move an object into the same cell.
