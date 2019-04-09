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


    def solveLevel(self):
        # We need to check the goal.
        plans = []
        for agt in self.agents:
            agt.plan(self.currentState)
            plans.append(agt.current_plan)
<<<<<<< HEAD
        #print('I am sending message to the server', file=sys.stderr, flush=True)
        while True:
            actions = list(zip(*plans))
            serverAction = [tuple(i['message'] for i in k) for k in actions[1:]]
            # print('I have made a list of actions', file=sys.stderr, flush=True)

            valid = self.executeAction(serverAction) ## keep the response from the server
            print(valid, file=sys.stderr, flush=True)
=======

        # print('I am sending message to the server', file=sys.stderr, flush=True)

        # actions = list(zip(*plans)) #won't work if plan are not the same length
        # serverAction = [tuple(i['message'] for i in k) for k in actions[1:]]
        nb_iter = 0
        while True:
            nb_iter += 1
            action_to_execute = self.getNextJointAction()
            valid = self.executeAction(action_to_execute) ## keep the response fro mthe server

            conflicting_agents = [i for i in range(len(valid)) if valid[i]=='false']
            if conflicting_agents != []:
                self.solveConflict(conflicting_agents, action_to_execute)
            if nb_iter % 10 == 0:

                self.agents[1].plan(self.currentState) # need a real replan function

    def solveConflict(self, conflicting_agents, actions):
        conflicting_agents= [0,1] # replace this by having function find the conflicting agents
        priority_agent = conflicting_agents.pop(0)
        action_of_priority_agent = actions[priority_agent]
        preconditions = action_of_priority_agent['action'].preconditions(*action_of_priority_agent['params'])
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


    def getNextJointAction(self):
        joint_action = []
        for agt in self.agents:
            if agt.current_plan != []:
                joint_action.append(agt.current_plan.pop(0))
            else:
                joint_action.append('NoOp')
        return joint_action

>>>>>>> eca870168f1e1540b7f711e6c8df5abc1ac26b9c
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
        print(actions_string, flush=True)
        print(actions_string, file=sys.stderr, flush=True)

        server_answer = sys.stdin.readline()[:-1].split(";")

        for i, answer in enumerate(server_answer):
            if answer == 'true':
                if jointAction[i] != 'NoOp':
                    jointAction[i]['action'].execute(self.currentState, jointAction[i]['params'])


        return server_answer
