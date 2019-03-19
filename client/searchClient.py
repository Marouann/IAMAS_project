import argparse
import re
import sys

class SearchClient:
    def __init__(self, server_messages):
        self.initial_state = []
        try:
            line = server_messages.readline().rstrip()
            while line:
                line = server_messages.readline().rstrip()
                self.initial_state.append(line)
        except Exception as ex:
            print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
            sys.exit(1)


def main():
    # Read server messages from stdin.
    server_messages = sys.stdin

    # Use stderr to print to console through server.
    print('SearchClient initializing. I am sending this using the error output stream.', file=sys.stderr, flush=True)
    print(server_messages, file=sys.stderr, flush=True)

    # Read level and create the initial state of the problem.
    client = SearchClient(server_messages)


if __name__ == '__main__':
    # Run client.
    main()
