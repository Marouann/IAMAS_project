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
    def __init__(self, initial_state: 'State', agents: '[Agent]', goal: '[Atom]'):
        self.currentState = initial_state
        self.agents = []
        self.goal = goal

        for agt in sorted(agents, key=lambda k: k['name']):
            agtAt = initial_state.findAgent(agt['name'])
            agent = Agent(agt['name'], agtAt, None, [Move, Push, Pull], agt['color'])
            self.agents.append(agent)

        # Here we need to assign the first goals to the agent

        # SAExample goal POSITIONS (Use SA.lvl)
        #self.agents[0].goal = Atom("BoxAt", "B1", (1, 1))

        # BFSLEVEL goal POSITIONS (Use BFStest.lvl)
        #self.agents[0].goal = Atom("BoxAt", "B1", (1, 4))
        #self.agents[1].goal = Atom("BoxAt", "B2", (5, 1))

        # BFSLEVEL with conflict goal POSITIONS (Use BFStestConflict.lvl)
        #self.agents[0].goal = Atom("BoxAt", "B1", (1, 4))
        #self.agents[1].goal = Atom("BoxAt", "B2", (5,1))


        # NO CONFLICT (Use MAExample.lvl)
        #self.agents[0].goal = Atom("BoxAt", "B1", (5, 1))
        #self.agents[1].goal = Atom("BoxAt", "B2", (1,10))

        # CONFLICT with two agents (Use MAExample.lvl)

        # CONFLICT with two agents and two boxes (Use MAConflictExample.lvl)
        #self.agents[0].goal = Atom("BoxAt", "B1", (1, 10)) # A goal
        #self.agents[1].goal = Atom("BoxAt", "B2", (5, 1))  # B goal

        # CONFLICT with two agents and two boxes (Use MAImpardist.lvl)
        self.agents[0].goal = Atom("BoxAt", "B1", (1, 10))  # A goal
        self.agents[1].goal = Atom("BoxAt", "B2", (5, 1))  # B goal


    '''
    What is current_plan?


    '''
    def solveLevel(self):
        # We need to check the goal.
        plans = []
        for agt in self.agents:
            agt.plan(self.currentState)
            plans.append(agt.current_plan)
            #print(agt, file=sys.stderr, flush=True) # agent
            #print(self.currentState, file=sys.stderr, flush=True) # state, rigid atoms, atoms 
            #print(agt.current_plan, file=sys.stderr, flush=True) # Current plan of actions for agent [action, param, message(name of action)]

        # print('I am sending message to the server', file=sys.stderr, flush=True)

        # actions = list(zip(*plans)) #won't work if plan are not the same length
        # serverAction = [tuple(i['message'] for i in k) for k in actions[1:]]

        # counter in while
        nb_iter = 0 
        # stop util reached goal
        while True:
            nb_iter += 1 
            
            # Gets the first actions from each agent (joint action on first row)
            action_to_execute = self.getNextJointAction()

            # Keep the response from the server ([true, false, ...])
            valid = self.executeAction(action_to_execute)

            # Gets the indexes (agent number) of server response (valid) for when action is not possible ([agt0, agt1, ...])
            conflicting_agents = [i for i in range(len(valid)) if valid[i]=='false']  

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
            #print("joint_action: ", file=sys.stderr, flush=True)
            #print(joint_action, file=sys.stderr, flush=True)
        return joint_action


    def solveConflict(self, conflicting_agents, actions):

        # Function that should return conflicting agents
        conflicting_agents= [0,1] ## replace this by having function find the conflicting agents

        # Set a priority agent (in this cases the first one in the array)
        priority_agent = conflicting_agents.pop(0)


        action_of_priority_agent = actions[priority_agent]

        preconditions = action_of_priority_agent['action'].preconditions(*action_of_priority_agent['params'])
        # TypeError: string indices must be integers when preconditions gets 'NoOp' I think.#
        unmet_preconditions = []

        for atom in preconditions:
            if atom not in self.currentState.atoms and atom not in self.currentState.rigid_atoms:
                unmet_preconditions.append(atom)

        conflict_solver = conflicting_agents[0]

        if unmet_preconditions != []:
            keep_goal = self.agents[conflict_solver].goal
            self.agents[conflict_solver].goal = unmet_preconditions[0]
            self.agents[conflict_solver].current_plan = []
            self.agents[conflict_solver].plan(self.currentState)
            # print(self.agents[conflict_solver].goal, file=sys.stderr, flush=True)
            # print(len(self.agents[conflict_solver].current_plan), file=sys.stderr, flush=True)
            self.executeAction(['NoOp', self.agents[conflict_solver].current_plan[0]]) # generalize this for more than 2 agents conflicting
            self.agents[conflict_solver].goal = keep_goal
            self.agents[conflict_solver].current_plan = []

            self.agents[priority_agent].current_plan = [action_of_priority_agent] + self.agents[priority_agent].current_plan
        else:
            self.executeAction([action_of_priority_agent,'NoOp']) # generalize this for more than 2 agents conflicting




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
        print(actions_string, flush=True) # send to server

        print(actions_string, file=sys.stderr, flush=True) # print out

        server_answer = sys.stdin.readline()[:-1].split(";")

        for i, answer in enumerate(server_answer):
            if answer == 'true':
                if jointAction[i] != 'NoOp':
                    jointAction[i]['action'].execute(self.currentState, jointAction[i]['params'])

        return server_answer
