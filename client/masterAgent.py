import argparse
import re
import sys
import numpy as np

from state import State
from atom import Atom
from agent import *
from action import *
from knowledgeBase import KnowledgeBase
from getLevel import getLevel


class MasterAgent:
    def __init__(self, initial_state: 'State', agents: '[Agent]', boxes: '[dict]'):
        self.currentState = initial_state
        self.agents = []
        self.boxes = boxes  # List of { 'name': Box, 'letter': char, 'color': color }
        self.goalsInAction = []

        for agt in sorted(agents, key=lambda k: k['name']):
            agtAt = initial_state.findAgent(agt['name'])
            agent = Agent(agt['name'], agtAt, None, [Move, Push, Pull, NoOp], agt['color'])
            self.agents.append(agent)

        # Here we need to assign the first goals to the agent

        # SAExample goal POSITIONS (Use SA.lvl)

        # self.agents[0].assignGoal(Atom("BoxAt", "B1", (1, 1)))

        # BFSLEVEL goal POSITIONS (Use BFStest.lvl)
        # self.agents[0].assignGoal(Atom("BoxAt", "B1", (1, 4)))
        # self.agents[1].assignGoal(Atom("BoxAt", "B2", (5, 1)))

        # BFSLEVEL with conflict goal POSITIONS (Use BFStestConflict.lvl)
        # self.agents[0].assignGoal(Atom("BoxAt", "B1", (1, 4)))
        # self.agents[1].assignGoal(Atom("BoxAt", "B2", (5,1)))

        # NO CONFLICT (Use MAExample.lvl)
        # self.agents[0].assignGoal(Atom("BoxAt", "B1", (5, 1)))
        # self.agents[1].assignGoal(Atom("BoxAt", "B2", (1,10)))

        # CONFLICT with two agents (Use MAExample.lvl)

        # CONFLICT with two agents and two boxes (Use MAConflictExample.lvl)

        # self.agents[0].assignGoal(Atom("BoxAt", "B1", (1, 10)) # A goal
        # self.agents[1].assignGoal(Atom("BoxAt", "B2", (5, 1)))  # B goal

        # CONFLICT with two agents and two boxes (Use MAImpardist.lvl)

        # self.agents[0].assignGoal(Atom("BoxAt", "B1", (1, 10)))  # A goal
        # self.agents[1].assignGoal(Atom("BoxAt", "B2", (5, 1)))  # B goal

    def assignGoals(self, agentsToReplan):
        (goalsToAssign, goalsMet) = self.currentState.getUnmetGoals()
        if agentsToReplan != []:
            print('\nFree agents : ' + str([agent.name for agent in agentsToReplan]), file=sys.stderr, flush=True)
            print('Goals unmet : ' + str(goalsToAssign), file=sys.stderr, flush=True)
            print('Goals already met : ' + str(goalsMet), file=sys.stderr, flush=True)
        
        boxesHandled = []
        # Boxes already placed on the goal
        for goal in goalsMet:
            boxOnGoal = self.currentState.findBox(goal['position'])
            boxesHandled.append(boxOnGoal.variables[0])

        # Boxes that are currently hadnled by agents
        for agent in self.agents:
            if agent.goal is not None:
                boxesHandled.append(agent.goal.variables[0])
                
        # Each agent that is passed to assignGoals either finished doing its job, or it's his 1st one
        # Hence we if self.goalsInAction contains agent.goal this job has been finished so we need to remove it
        for agent in agentsToReplan:
            if agent.goal in self.goalsInAction:
                self.goalsInAction.remove(agent.goal)

        for goal in self.goalsInAction:
            if goal in goalsToAssign:
                goalsToAssign.remove(goal)

        sortedGoals = self.priorytazeGoals(goalsToAssign)

        if sortedGoals != []:
            for agent in agentsToReplan:
                if agent.current_plan != []:

                    print(agent.name, agent.current_plan[0], file=sys.stderr, flush=True)
                else:
                    print('Agent', agent.name, 'has no plan!', file=sys.stderr, flush=True)

                if agent.occupied == False:
                    print('Agent', agent.name, 'is not occupied!', file=sys.stderr, flush=True)
                    for goal in sortedGoals:
                        if agent.goal is not None:
                            print('Agent already has a goal, continue: ' + str(goal), file=sys.stderr, flush=True)
                            continue
                        if goal in self.goalsInAction:
                            print('Goal has already been assigned : ' + str(goal), file=sys.stderr, flush=True)
                            continue
                        possibleBoxes = []
                        for box in self.boxes:
                            if box['color'] == agent.color and \
                                    box['letter'] == goal['letter'] and \
                                    box['name'] not in boxesHandled:
                                possibleBoxes.append(box)

                        goalNotAssigned = True
                        while goalNotAssigned and possibleBoxes != []:
                            box = possibleBoxes.pop()
                            boxAlreadyPlaced = False
                            for goalmet in goalsMet:
                                boxPlaced = self.currentState.findBox(goalmet['position'])
                                if boxPlaced.variables[0] == box['name']:
                                    boxAlreadyPlaced = True

                            if not boxAlreadyPlaced:
                                agent.assignGoal(Atom("BoxAt", box['name'], goal['position']))
                                self.goalsInAction.append(goal)
                                boxesHandled.append(box['name'])
                                goalNotAssigned = False
                                if not agent.goal in self.currentState.atoms:
                                    agent.plan(self.currentState)

        for agent in agentsToReplan:
            print('agent: ' + str(agent.name) + ', has goal: ' + str(agent.goal), file=sys.stderr, flush=True)

            # goalNotAssigned = True
            # for goal in goalsToAssign:
            #     if goalNotAssigned:
            #         box = next((box for box in possibleBoxes if box['letter'] == goal['letter'] and), None)
            #         if box != None:
            #             agent.assignGoal(Atom("BoxAt", box['name'], goal['position']))
            #             # print(agent.occupied, file=sys.stderr, flush=True)
            #             # print(str(agent.goal), file=sys.stderr, flush=True)
            #             goalNotAssigned = False
            #             if not agent.goal in self.currentState.atoms:
            #                 agent.plan(self.currentState)

    ##What is current_plan?

    def solveLevel(self):
        # We need to check the goal.
        self.assignGoals(self.agents)
        # print(agt, file=sys.stderr, flush=True) # agent
        # print(self.currentState, file=sys.stderr, flush=True) # state, rigid atoms, atoms
        # print(agt.current_plan, file=sys.stderr, flush=True) # Current plan of actions for agent [action, param, message(name of action)]

        # print('I am sending message to the server', file=sys.stderr, flush=True)

        # actions = list(zip(*plans)) #won't work if plan are not the same length
        # serverAction = [tuple(i['message'] for i in k) for k in actions[1:]]

        # counter in while
        nb_iter = 0
        # stop util reached goal
        while self.currentState.getUnmetGoals()[0] != []:
            # First we loop over agent to free them if their goal are met

            # for agent in self.agents:
            #     if agent.goal in self.currentState.atoms:
            #         agent.occupied = False

            # Then if at least one agent is free we assign goals
            # The method assign goals, assign goal only to free agent

            self.assignGoals([agent for agent in self.agents if agent.occupied == False])
            nb_iter += 1

            # Gets the first actions from each agent (joint action on first row)
            action_to_execute = self.getNextJointAction()

            # Keep the response from the server ([true, false, ...])
            valid = self.executeAction(action_to_execute)

            print(valid, file=sys.stderr, flush=True)  # agent

            # Gets the indexes (agent number) of server response (valid) for when action is not possible ([agt0, agt1, ...])
            conflicting_agents = [i for i in range(len(valid)) if valid[i] == 'false']

            # If there exists conflicts (false in valid array) then run solveConflict function with the conflicting agents
            if conflicting_agents != []:
                self.solveConflict(conflicting_agents, action_to_execute)

            # Replan after (nb_iter % 'x') 'x' interations (Need a real replan function)
            # Change x parameter in order to solve in less states
            if nb_iter % 10 == 0:
                self.agents[1].plan(self.currentState)

    def getNextJointAction(self):
        # initialize joint_action with 'NoOp' of length number of agents ['NoOp', 'NoOp', 'NoOp', ...]
        joint_action = ['NoOp'] * len(self.agents)

        for i, agt in enumerate(self.agents):
            # If there are still actions in current plan pop the first action and
            # agt.current_plan = agt_x ['Action0', 'Action1', 'Action2', ...]

            if agt.current_plan != []:
                # agt.current_plan.pop(0) = 'Action0'
                # joint_action = ['NoOp', 'NoOp', 'NoOp', ...]
                # joint_action[0] = ['agt0.Action0', 'NoOp', 'NoOp', ... ]
                # joint_action[1] = ['agt0.Action0', 'agt1.Action0', 'NoOp', ... ] ...
                joint_action[i] = agt.current_plan.pop(0)
                # print("joint_action: ", file=sys.stderr, flush=True)
            # print(joint_action, file=sys.stderr, flush=True)
        return joint_action

    def priorytazeGoals(self, goals):
        # Sort goals 1st by number of free neighbour fields, then by number of neighbour goals)
        sortedGoals = sorted(goals,
                                key=lambda x: (self.currentState.getNeithbourFieldsWithoutGoals(x["position"]).__len__(),
                                self.currentState.getNeithbourGoals(x["position"]).__len__()))

        return sortedGoals

    def solveConflict(self, conflicting_agents, actions):
        print('solve conflict', file=sys.stderr, flush=True)
        # Function that should return conflicting agents
        conflicting_agents = [0, 1]  ## replace this by having function find the conflicting agents

        # Set a priority agent (in this cases the first one in the array)

        # Previous
        # priority_agent = conflicting_agents.pop(0)

        priority_agent = 0  # replace with a function that return the agent to prioritize

        #####
        #####
        action_of_priority_agent = actions[priority_agent]

        preconditions = action_of_priority_agent['action'].preconditions(*action_of_priority_agent['params'])
        # TypeError: string indices must be integers when preconditions gets 'NoOp' I think.#
        unmet_preconditions = []

        for atom in preconditions:
            if atom not in self.currentState.atoms and atom not in self.currentState.rigid_atoms:
                unmet_preconditions.append(atom)

        # Previous
        # conflict_solver = conflicting_agents[0]

        conflict_solver = 1  # replace with a function that return the agent that has to change its goal

        if unmet_preconditions != []:
            keep_goal = self.agents[conflict_solver].goal
            self.agents[conflict_solver].assignGoal(unmet_preconditions[0])
            self.agents[conflict_solver].current_plan = []
            self.agents[conflict_solver].plan(self.currentState)
            # print(self.agents[conflict_solver].goal, file=sys.stderr, flush=True)
            print(self.agents[conflict_solver].current_plan, file=sys.stderr, flush=True)

            actionsToResolveConflicts = ['NoOp' for i in range(len(self.agents))]
            actionsToResolveConflicts[conflict_solver] = self.agents[conflict_solver].current_plan[0]
            self.executeAction(actionsToResolveConflicts)  # generalize this for more than 2 agents conflicting

            self.agents[conflict_solver].assignGoal(keep_goal)
            self.agents[conflict_solver].current_plan = []

            self.agents[priority_agent].current_plan = [action_of_priority_agent] + self.agents[
                priority_agent].current_plan
        else:
            actionsToResolveConflicts = ['NoOp' for i in range(len(self.agents))]
            actionsToResolveConflicts[priority_agent] = action_of_priority_agent

            self.executeAction(actionsToResolveConflicts)  # generalize this for more than 2 agents conflicting

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
        for agent_action in jointAction:
            if agent_action != 'NoOp':
                actions_string += agent_action['message']
                actions_string += ';'
            else:
                actions_string += agent_action
                actions_string += ';'
        actions_string = actions_string[:-1]  # remove last ';' from the string

        # retrieve answer from server and separate answer for specific action
        # [:-1] is only to remove the '\n' at the end of response
        print(actions_string, file=sys.stderr, flush=True)  # print out
        print(actions_string, flush=True)  # send to server

        server_answer = sys.stdin.readline()[:-1].split(";")

        for i, answer in enumerate(server_answer):
            if answer == 'true':
                if jointAction[i] != 'NoOp':
                    jointAction[i]['action'].execute(self.currentState, jointAction[i]['params'])

        for agent in self.agents:
            if agent.goal in self.currentState.atoms:
                agent.occupied = False
                agent.current_plan = []

        for agent in self.agents:
            if agent.goal in self.currentState.atoms:
                agent.occupied = False
                agent.current_plan = []
                agent.goal = None

        return server_answer
