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
from masterAgent import MasterAgent

class SearchClient:
    def __init__(self, server_messages):
        self.domain = None
        self.levelName = None
        self.masterAgent = None

        # We get the level information from the incoming stream.
        level = getLevel(server_messages)

        self.domain = level['domain']
        self.levelName = level['levelName']

        self.masterAgent = MasterAgent(level['initial_state'], level['agents']) # level['goals'], level['boxes']

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
    # agt1 = Agent('1', (5,3), Atom("BoxAt","B2", (1,10)), [Move, Push, Pull], "green")
    # agt0 = Agent('0', (1,8), Atom("BoxAt","B1", (5,1)), [Move, Push, Pull], "red")

    ## PRODUCEs CONFLICT
    # agt1 = Agent('1', (5,3), Atom("BoxAt","B2", (5,1)), [Move, Push, Pull], "green")
    # agt0 = Agent('0', (1,8), Atom("BoxAt","B1", (1,10)), [Move, Push, Pull], "red")

    # currentState = client.initial_state

    # print(currentState, file=sys.stderr, flush=True)
    # agt1.plan(currentState)
    # agt0.plan(currentState)

    # actions = list(zip(agt0.current_plan, agt1.current_plan))
    # serverAction = [(action1['message'], action2['message']) for (action1, action2) in actions]
    # valid = client.executeAction(serverAction)

    client.masterAgent.solveLevel()


if __name__ == '__main__':
    # Run client.
    main()
