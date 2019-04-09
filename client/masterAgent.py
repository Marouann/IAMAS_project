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
    def __init__(self, initial_state: 'State', agents, goal):
        self.currentState = initial_state
        self.agents = []
        self.goal = goal

        for agt in sorted(agents, key=lambda k: k['name']):
            agtAt = initial_state.findAgent(agt['name'])
            agent = Agent(agt['name'], agtAt, None, [Move, Push, Pull], agt['color'])
            self.agents.append(agent)

        # Here we need to assign the first goals to the agent
        self.agents[0].goal = Atom('BoxAt', 'B1', (1,10))
        self.agents[1].goal = Atom("BoxAt","B2", (5,1))

    def solveLevel(self):
        # We need to check the goal.
        plans = []
        for agt in self.agents:
            agt.plan(self.currentState)
            plans.append(agt.current_plan)
        print('I am sending message to the server', file=sys.stderr, flush=True)

        actions = list(zip(*plans))
        serverAction = [tuple(i['message'] for i in k) for k in actions[1:]]
        print('I have made a list of actions', file=sys.stderr, flush=True)

        valid = self.executeAction(serverAction)

    '''
    actionList is a 2D array of actions (size number_action_to_execute * number_of_agents).
        - a row corresponds to a joint action
        - each col represents action of a specific agent

    return successive result of the server to actions, same size as input
    '''

    def executeAction(self, actionsList):
        print('I am executing actions', file=sys.stderr, flush=True)

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
            print('Waiting for server', file=sys.stderr, flush=True)

            server_answer.append(sys.stdin.readline()[:-1].split(";"))
            print(server_answer, file=sys.stderr, flush=True)

            # We need to update the masterAgent.currentState in case there is a conflict

        return server_answer
