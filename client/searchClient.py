import argparse
import sys
from masterAgent import *
from utils import level_adjacency, get_level
from Multi import *
import time


class SearchClient:
    def __init__(self, server_messages):
        self.domain = None
        self.levelName = None
        self.masterAgent = None

        # We get the level information from the incoming stream.
        level = get_level(server_messages)
        #print(level['initial_state'])
        #print(level['initial_state'])
        start_time = time.time()
        level_adjacency(level['initial_state'])
        #level['initial_state'].rigid_atoms += multiprocess_adjacency(level['initial_state']) ## state, max rows and max cols in level
        print('That took {} seconds for normal'.format(time.time() - start_time), file=sys.stderr, flush=True)

        start_time = time.time()
        multiprocess_adjacency(level['initial_state'])
        #level['initial_state'].rigid_atoms += multiprocess_adjacency(level['initial_state']) ## state, max rows and max cols in level
        print('That took {} seconds for multi'.format(time.time() - start_time), file=sys.stderr, flush=True)
        raise BaseException()
        self.domain = level['domain']
        self.levelName = level['levelName']

        self.masterAgent = MasterAgent(level['initial_state'], level['agents'],
                                       level['boxes'])  # level['goals'], level['boxes']


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
