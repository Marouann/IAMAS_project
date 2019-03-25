import argparse
import re
import sys
from newState import State
from atom import Atom

class SearchClient:
    def __init__(self, server_messages):
        self.initial_state = None
        self.domain = None
        self.levelName = None

        try:
            line = server_messages.readline()
            color = False
            initial = False
            goal = False
            row = 0

            # Initialize the predicates
            predicates = []

            currentBox = 1
            currentGoal = 1

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
                    color = splittedLine[0]
                    IsColor = Atom('IsColor', [color])
                    predicates.append(IsColor)

                    objects = splittedLine[1].split(",")
                    for obj in objects:
                        Color = Atom('Color', [obj, color])
                        predicates.append(Color)

                if initial:
                    for col, char in enumerate(line):
                        if char == '+':
                            a=1
                        elif char in "0123456789":
                            AgentAt = Atom('AgentAt', [char, row, col])
                            predicates.append(AgentAt)

                            L = Atom('L', [row, col])
                            predicates.append(L)
                        elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                            Box = Atom('Box', [currentBox])
                            predicates.append(Box)

                            Letter = Atom('Letter', [currentBox, char])
                            predicates.append(Letter)

                            BoxAt = Atom('BoxAt', [currentBox, row, col])
                            predicates.append(BoxAt)

                            L = Atom('L', [row, col])
                            predicates.append(L)

                            currentBox += 1
                        elif char == ' ':
                            # Free cell.
                            FreeL = Atom('Free', [row, col])
                            predicates.append(FreeL)

                            L = Atom('L', [row, col])
                            predicates.append(L)
                            pass
                        else:
                            print('Error, read invalid level character: {}'.format(char), file=sys.stderr, flush=True)
                            sys.exit(1)
                    row += 1

                if goal:
                    for col, char in enumerate(line):
                        if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                            Goal = Atom('Goal', [currentGoal])
                            predicates.append(Box)

                            Letter = Atom('Letter', [currentGoal, char.lower()])
                            predicates.append(Letter)

                            GoalAt = Atom('GoalAt', [currentGoal, row, col])
                            predicates.append(BoxAt)

                            currentGoal += 1

                    row += 1

                line = server_messages.readline().rstrip()

            self.initial_state = State('s0', predicates)
            for i in self.initial_state.atoms:
                print(str(i), file=sys.stderr, flush=True)
            print(str(self.initial_state), file=sys.stderr, flush=True)

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
    # actions = [['Move(W)','Move(E)'], ['Move(W)','Move(E)'], ['Move(W)','Move(E)'], ['Move(W)','Move(E)']]
    # print(client.executeAction(actions), file=sys.stderr, flush=True)


if __name__ == '__main__':
    # Run client.
    main()
