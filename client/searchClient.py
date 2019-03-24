import argparse
import re
import sys
from state import State

class SearchClient:
    def __init__(self, server_messages):
        self.initial_state = None
        self.domain = None
        self.levelName = None
        self.colors = {}

        try:
            line = server_messages.readline()
            color = False
            initial = False
            goal = False
            row = 0

            # Initialize the state
            self.initial_state = State()
            while line != "#end":
                if line == '#domain':
                    line = server_messages.readline().rstrip()
                    self.domain= line
                elif line == "#levelname":
                    line = server_messages.readline().rstrip()
                    self.levelName = line
                elif line == "#colors":
                    color = True
                    line = server_messages.readline().rstrip()
                elif line == "#initial":
                    color = False
                    initial = True

                    row = 0
                    line = server_messages.readline().rstrip()


                elif line == "#goal":
                    initial = False
                    goal = True

                    row = 0
                elif line == "#end":
                    goal = False

                if color:
                    splittedLine = line.split(":")
                    self.colors[splittedLine[0]] = splittedLine[1].split(",")
                if initial:
                    self.initial_state.walls.append([False for _ in range(len(line))])
                    self.initial_state.boxes.append([None for _ in range(len(line))])

                    for col, char in enumerate(line):
                        if char == '+': self.initial_state.walls[row][col] = True
                        elif char in "0123456789":
                            self.initial_state.agents[char] = { "row": row, "col": col }
                        elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                            self.initial_state.boxes[row][col] = char
                        elif char == ' ':
                            # Free cell.
                            pass
                        else:
                            print('Error, read invalid level character: {}'.format(char), file=sys.stderr, flush=True)
                            sys.exit(1)
                    row += 1

                if goal:
                    self.initial_state.goals.append([None for _ in range(len(line))])
                    for col, char in enumerate(line):
                        if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ": self.initial_state.goals[row][col] = char

                    row += 1

                line = server_messages.readline().rstrip()


        except Exception as ex:
            print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
            sys.exit(1)

    '''
    actionList is a 2D array of actions (size number_action_to_execute * number_of_agents).
        - a row corresponds to a joint action
        - each col represents action of a specific agent

    return successive result of the server to actions, same size as input
    '''
    def executeAction(self,actionsList):
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

    # test actions execution
    actions = [['Move(W)','Move(E)'], ['Move(W)','Move(E)'], ['Move(W)','Move(E)'], ['Move(W)','Move(E)']]
    #test actions execution on the SAExample
    #actions = [['Move(W)'], ['Pull(E,S)'], ['NoOp'], ['Push(W,N)']]
    print(client.executeAction(actions), file=sys.stderr, flush=True)


if __name__ == '__main__':
    # Run client.
    main()
