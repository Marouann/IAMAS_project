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
        self.boxes = boxes # List of { 'name': Box, 'letter': char, 'color': color }
        self.goalsAssigned = []

        for agt in sorted(agents, key=lambda k: k['name']):
            agtAt = initial_state.findAgent(agt['name'])
            agent = Agent(agt['name'], agtAt, None, [Move, Push, Pull], agt['color'])
            self.agents.append(agent)

        # Here we need to assign the first goals to the agent

        # SAExample goal POSITIONS (Use SA.lvl)
        #self.agents[0].assignGoal(Atom("BoxAt", "B1", (1, 1)))

        # BFSLEVEL goal POSITIONS (Use BFStest.lvl)
        #self.agents[0].assignGoal(Atom("BoxAt", "B1", (1, 4)))
        #self.agents[1].assignGoal(Atom("BoxAt", "B2", (5, 1)))

        # BFSLEVEL with conflict goal POSITIONS (Use BFStestConflict.lvl)
        #self.agents[0].assignGoal(Atom("BoxAt", "B1", (1, 4)))
        #self.agents[1].assignGoal(Atom("BoxAt", "B2", (5,1)))


        # NO CONFLICT (Use MAExample.lvl)
        #self.agents[0].assignGoal(Atom("BoxAt", "B1", (5, 1)))
        #self.agents[1].assignGoal(Atom("BoxAt", "B2", (1,10)))

        # CONFLICT with two agents (Use MAExample.lvl)

        # CONFLICT with two agents and two boxes (Use MAConflictExample.lvl)
        #self.agents[0].assignGoal(Atom("BoxAt", "B1", (1, 10)) # A goal
        #self.agents[1].assignGoal(Atom("BoxAt", "B2", (5, 1)))  # B goal

        # CONFLICT with two agents and two boxes (Use MAImpardist.lvl)

        # self.agents[0].assignGoal(Atom("BoxAt", "B1", (1, 10)))  # A goal
        # self.agents[1].assignGoal(Atom("BoxAt", "B2", (5, 1)))  # B goal

    def assignGoals(self, agents):
        (goalsToAssign, goalsMet) = self.currentState.getUnmetGoals()

        if agents != []:
            print('\nFree agents : ' + str([agent.agt for agent in agents]), file=sys.stderr, flush=True)
            print('Goals unmet : ' + str(goalsToAssign), file=sys.stderr, flush=True)
            print('Goals already met : ' + str(goalsMet), file=sys.stderr, flush=True)

        if goalsToAssign != []:
            for agent in agents:
                if agent.current_plan != []:
                    print(agent.agt, agent.current_plan[0], file=sys.stderr, flush=True)

                if agent.occupied == False:
                    for goal in goalsToAssign:
                        possibleBoxes = []
                        for box in self.boxes:
                            if box['color'] == agent.color and box['letter'] == goal['letter']:
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
                                goalNotAssigned = False
                                if not agent.goal in self.currentState.atoms:
                                    agent.plan(self.currentState)
                            

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


    def solveLevel(self):
        # We need to check the goal.
        self.assignGoals(self.agents)
            #print(agt, file=sys.stderr, flush=True) # agent
            #print(self.currentState, file=sys.stderr, flush=True) # state, rigid atoms, atoms 
            #print(agt.current_plan, file=sys.stderr, flush=True) # Current plan of actions for agent [action, param, message(name of action)]

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
            actions_to_execute = self.getNextJointAction()

            # Keep the response from the server ([true, false, ...])
            valid = self.executeAction(actions_to_execute)
            print('Server response : ' + str(valid), file=sys.stderr, flush=True)

            # 'agents_with_conflit': List of agents which cannot execute their actions (e.g [agt0, agt1, agt6])
            agents_with_conflit = [i for i in range(len(valid)) if valid[i]=='false']  
            print('agents_with_conflit : ' + str(agents_with_conflit),file=sys.stderr, flush=True)

            # If 'agents_with_conflit' not empty then solve conflict
            if agents_with_conflit != []:
                self.solveConflict(agents_with_conflit, actions_to_execute)

            # Replan after (nb_iter % 'x') 'x' interations (Need a real replan function)
            # Change x parameter in order to solve in less states
            if nb_iter % 10 == 0:                                             # make dinamic replanner #
                self.agents[1].plan(self.currentState)

    '''
    Returns joint_action: the next actions to be executed for each agent
    '''
    def getNextJointAction(self):
        # initialize joint_action with 'NoOp' of length number of agents ['NoOp', 'NoOp', 'NoOp', ...]
        joint_action = ['NoOp'] * len(self.agents)
        for i, agt in enumerate(self.agents):
            # If there are still actions in current plan pop the first action and
            if agt.current_plan != []:
                joint_action[i] = agt.current_plan.pop(0)      
            # print(joint_action, file=sys.stderr, flush=True)
        return joint_action

    def solveConflict(self, agents_with_conflit, actions):
        print('solve conflict', file=sys.stderr, flush=True)
        print('actions : ' + str(actions), file=sys.stderr, flush=True)
        # Function that should return conflicting agents
                                                                # replace this by having function find the conflicting agents #
        # two agents in conflict with each other                                  
        agents_in_conflict = agents_with_conflit

        # choose an agent with a conflict
        agent_with_conflit = agents_with_conflit[0]

        # get action from that chosen agent
        action_agent_with_conflict = actions[0]
        
        # get location were he wanted to go
        location_agt_to = action_agent_with_conflict['params'][2] # were they want to go locations
        print('location_agt_to : ' + str(location_agt_to), file=sys.stderr, flush=True)

        conflicting_agent = []
        # goes through all existing 
        # get location from agent

        # find what is in that location which is conficting with with chosen agent
        for agent in self.agents:
            
            # get agent current location
            location_agt_from = self.currentState.findAgent(agent.agt)
            print('location_agt_from : ' + str(location_agt_from), file=sys.stderr, flush=True)

            # compare location_agt_to with location_agt_from 
            if location_agt_to == location_agt_from:
                # stores agent conflicting with chosen agent
                conflicting_agent = int(agent.agt)
                #print('conflicting_agent : ' + str(conflicting_agent), file=sys.stderr, flush=True)

        # two agents in conflict with each other
        agents_in_conflict = [agent_with_conflit, conflicting_agent]
        print('agents_in_conflict : ' + str(agents_in_conflict), file=sys.stderr, flush=True)


        # Set a priority agent (in this cases the first one in the array)
        
        # Previous
        priority_agent = agents_in_conflict.pop(0)
        #priority_agent = 0                                     # replace with a function that return the agent to prioritize

        action_of_priority_agent = actions[priority_agent]

        preconditions = action_of_priority_agent['action'].preconditions(*action_of_priority_agent['params'])
        # TypeError: string indices must be integers when preconditions gets 'NoOp' I think.#
        unmet_preconditions = []

        for atom in preconditions:
            if atom not in self.currentState.atoms and atom not in self.currentState.rigid_atoms:
                unmet_preconditions.append(atom)


        # Previous
        conflict_solver = agents_in_conflict[0]
        #conflict_solver = 1                             # replace with a function that return the agent that has to change its goal

        if unmet_preconditions != []:
            keep_goal = self.agents[conflict_solver].goal
            self.agents[conflict_solver].assignGoal(unmet_preconditions[0])
            self.agents[conflict_solver].current_plan = []
            self.agents[conflict_solver].plan(self.currentState)
            # print(self.agents[conflict_solver].goal, file=sys.stderr, flush=True)
            # print(self.agents[conflict_solver].current_plan, file=sys.stderr, flush=True)

            actionsToResolveConflicts = ['NoOp' for i in range(len(self.agents))]
            actionsToResolveConflicts[conflict_solver] = self.agents[conflict_solver].current_plan[0]
            self.executeAction(actionsToResolveConflicts) # generalize this for more than 2 agents conflicting
            self.agents[conflict_solver].assignGoal(keep_goal)
            self.agents[conflict_solver].current_plan = []

            self.agents[priority_agent].current_plan = [action_of_priority_agent] + self.agents[priority_agent].current_plan
        else:
            actionsToResolveConflicts = ['NoOp' for i in range(len(self.agents))]
            actionsToResolveConflicts[priority_agent] = action_of_priority_agent
            self.executeAction(actionsToResolveConflicts) # generalize this for more than 2 agents conflicting


    '''
    actionList is a 2D array of actions (size number_action_to_execute * number_of_agents).
        - a row corresponds to a joint action
        - each col represents action of a specific agent

    return successive result of the server to actions, same size as input
    '''


    def executeAction(self, jointAction):
        #print('I am executing actions', file=sys.stderr, flush=True)

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
        print(actions_string, file=sys.stderr, flush=True) # print out
        print(actions_string, flush=True) # send to server

        server_answer = sys.stdin.readline()[:-1].split(";")

        for i, answer in enumerate(server_answer):
            if answer == 'true':
                if jointAction[i] != 'NoOp':
                    jointAction[i]['action'].execute(self.currentState, jointAction[i]['params'])
        
        for agent in self.agents:
            if agent.goal in self.currentState.atoms:
                agent.occupied = False
                agent.current_plan = []

        return server_answer
