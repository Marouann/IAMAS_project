import argparse
import sys
from masterAgent2 import *
from utils import level_adjacency, get_level, identify_cells
from Tracker import Tracker


sys.setrecursionlimit(10000)

class SearchClient:
    def __init__(self, server_messages):
        self.domain = None
        self.levelName = None
        self.masterAgent = None

        # We get the level information from the incoming stream.
        level = get_level(server_messages)
        level['initial_state'].rigid_atoms += level_adjacency(level['initial_state']) ## state, max rows and max cols in level
        cell_types = identify_cells(level['initial_state'], level['rows'], level['cols'])
        level['initial_state'].safe_cells = cell_types['safe']
        level['initial_state'].tunnel_cells = cell_types['tunnel']
        self.domain = level['domain']
        self.levelName = level['levelName']
        self.masterAgent = MasterAgent(level['initial_state'], level['agents'],
                                       level['boxes'])


def main():
    # We first declare our name. The server will receive it and be ready to start with us.
    print('Best group', flush=True)
    # Read server messages from stdin.
    server_messages = sys.stdin

    # Use stderr to print to console through server.
    print('SearchClient initializing. I am sending this using the error output stream.', file=sys.stderr, flush=True)

    # Read level and create the initial state of the problem.
    client = SearchClient(server_messages)
    client.masterAgent.solveLevel()


if __name__ == '__main__':
    # Run client.
    main()
