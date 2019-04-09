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
        self.agents[0].goal = Atom("BoxAt", "B1", (1, 9))  # A goal
        self.agents[1].goal = Atom("BoxAt", "B2", (5, 1))  # B goal


    def solveLevel(self):
        # We need to check the goal.
        plans = []
        for agt in self.agents:
            agt.plan(self.currentState)
            plans.append(agt.current_plan)
        #print('I am sending message to the server', file=sys.stderr, flush=True)
        while True:
            actions = list(zip(*plans))
            serverAction = [tuple(i['message'] for i in k) for k in actions[1:]]
            # print('I have made a list of actions', file=sys.stderr, flush=True)

            valid = self.executeAction(serverAction) ## keep the response from the server
            print(valid, file=sys.stderr, flush=True)
    '''
    actionList is a 2D array of actions (size number_action_to_execute * number_of_agents).
        - a row corresponds to a joint action
        - each col represents action of a specific agent

    return successive result of the server to actions, same size as input
    '''

    def executeAction(self, actionsList):
        #print('I am executing actions', file=sys.stderr, flush=True)

        server_answer = []
        for jointAction in actionsList:
            actions_string = ""
            for agent_action in jointAction:
                actions_string += agent_action
                actions_string += ";"
            actions_string = actions_string[:-1]  # remove last ';' from the string

            # retrieve answer from server and separate answer for specific action
            # [:-1] is only to remove the '\n' at the end of response
            print(actions_string, flush=True)

            server_answer.append(sys.stdin.readline()[:-1].split(";"))

            # We need to update the masterAgent.currentState in case there is a conflict

        return server_answer
