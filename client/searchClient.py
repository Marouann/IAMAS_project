import argparse
import re
import sys
import numpy as np
import asyncio

from state import State
from atom import Atom
from agent import Agent
from action import *
from knowledgeBase import KnowledgeBase
from getLevel import getLevel
from masterAgent import *


class SearchClient:
    def __init__(self, server_messages):
        self.domain = None
        self.levelName = None
        self.masterAgent = None

        # We get the level information from the incoming stream.
        level = getLevel(server_messages)
        self.domain = level['domain']
        self.levelName = level['levelName']

        self.masterAgent = MasterAgent(level['initial_state'], level['agents'],
                                       level['boxes'])  # level['goals'], level['boxes']


async def main():
    # We first declare our name. The server will receive it and be ready to start with us.
    print('Best group', flush=True)
    # Read server messages from stdin.
    server_messages = sys.stdin
    #server_messages = open('../MAMoreGoalsSameColor.lvl')

    # Use stderr to print to console through server.
    print('SearchClient initializing. I am sending this using the error output stream.', file=sys.stderr, flush=True)

    # Read level and create the initial state of the problem.
    client = SearchClient(server_messages)

    await client.masterAgent.solveLevel()


if __name__ == '__main__':
    # Run client.
    asyncio.run(main())
