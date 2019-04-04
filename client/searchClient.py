import argparse
import re
import sys
import numpy as np

from state import State
from atom import Atom
from agent import Agent
from action import *
from knowledgeBase import KnowledgeBase
from getLevel import getLevel

class SearchClient:
    def __init__(self, server_messages):
        self.initial_state = None
        self.domain = None
        self.levelName = None

        level = getLevel(server_messages)

        self.initial_state = level['initial_state']
        self.domain = level['domain']
        self.levelName = level['levelName']


    '''
    actionList is a 2D array of actions (size number_action_to_execute * number_of_agents).
        - a row corresponds to a joint action
        - each col represents action of a specific agent

    return successive result of the server to actions, same size as input
    '''
    def executeAction(self, actionsList):
        server_answer = []
        for jointAction in actionsList:
            actions_string = ""
            for agent_action in jointAction:
                actions_string += agent_action
                actions_string += ";"
            actions_string = actions_string[:-1] # remove last ';' from the string
            print(actions_string, flush=True) # send action to server

            # retrieve answer from server and separate answer for specific action
            # [:-1] is only to remove the '\n' at the end of response
            server_answer.append(sys.stdin.readline()[:-1].split(";"))

        return server_answer

def main():
    # We first declare our name. The server will receive it and be ready to start with us.
    print('Best group', flush=True)

    # Read server messages from stdin.
    server_messages = sys.stdin

    # Use stderr to print to console through server.
    print('SearchClient initializing. I am sending this using the error output stream.', file=sys.stderr, flush=True)

    # Read level and create the initial state of the problem.
    client = SearchClient(server_messages)


    ## DOES NOT PRODUCE CONFLICT
    agt1 = Agent('1', (5,3), Atom("BoxAt","B2", (1,10)), [Move, Push, Pull], "green")
    agt0 = Agent('0', (1,8), Atom("BoxAt","B1", (5,1)), [Move, Push, Pull], "red")

    ## PRODUCEs CONFLICT
    # agt1 = Agent('1', (5,3), Atom("BoxAt","B2", (5,1)), [Move, Push, Pull], "green")
    # agt0 = Agent('0', (1,8), Atom("BoxAt","B1", (1,10)), [Move, Push, Pull], "red")
    
    currentState = client.initial_state

    print(currentState, file=sys.stderr, flush=True)
    agt1.plan(currentState)
    agt0.plan(currentState)

    actions = list(zip(agt0.current_plan, agt1.current_plan))
    valid = client.executeAction(actions)


if __name__ == '__main__':
    # Run client.
    main()
