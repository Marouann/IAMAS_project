import argparse
import re
import sys
import numpy as np
from newState import State
from atom import Atom
from agent import Agent
from action import *

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
            atoms = []
            rigidAtoms = []
            boxColors = {}

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
                    rigidAtoms.append(IsColor)

                    objects = splittedLine[1].split(",")
                    for obj in objects:
                        boxColors[obj.replace(' ', '')] = color

                if initial:
                    for col, char in enumerate(line):
                        if char == '+':
                            a=1
                        elif char in "0123456789":
                            AgentAt = Atom('AgentAt', [char, (row, col)])
                            atoms.append(AgentAt)

                            Color = Atom('Color', [char, boxColors[char]])
                            rigidAtoms.append(Color)

                        elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                            Box = 'B' + str(currentBox)

                            Color = Atom('Color', [Box, boxColors[char]])
                            rigidAtoms.append(Color)

                            Letter = Atom('Letter', [Box, char])
                            rigidAtoms.append(Letter)

                            BoxAt = Atom('BoxAt', [Box, (row, col)])
                            atoms.append(BoxAt)

                            currentBox += 1
                        elif char == ' ':
                            # Free cell.
                            FreeL = Atom('Free', [(row, col)])
                            atoms.append(FreeL)
                            pass
                        else:
                            print('Error, read invalid level character: {}'.format(char), file=sys.stderr, flush=True)
                            sys.exit(1)

                        if char != '+':
                            if row > 0 and col < len(previousLine):
                                if previousLine[col] != '+':
                                    rigidAtoms.append(Atom('Neighbour', [(row - 1, col), (row, col)]))
                                    rigidAtoms.append(Atom('Neighbour', [(row, col), (row - 1, col)]))
                            if col > 0:
                                if line[col - 1] != '+':
                                    rigidAtoms.append(Atom('Neighbour', [(row, col), (row, col - 1)]))
                                    rigidAtoms.append(Atom('Neighbour', [(row, col - 1), (row, col)]))


                    row += 1

                if goal:
                    for col, char in enumerate(line):
                        if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                            Goal = 'G' + str(currentGoal)

                            Letter = Atom('Letter', [Goal, char.lower()])
                            rigidAtoms.append(Letter)

                            GoalAt = Atom('GoalAt', [Goal, (row, col)])
                            rigidAtoms.append(GoalAt)

                            currentGoal += 1

                    row += 1

                previousLine = line
                line = server_messages.readline().rstrip()

            self.initial_state = State('s0', atoms, rigidAtoms)
            for i in self.initial_state.rigid_atoms:
                print(str(i), file=sys.stderr, flush=True)
            for i in self.initial_state.atoms:
                print(str(i), file=sys.stderr, flush=True)

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
    # print('Execute some actions', file=sys.stderr, flush=True)
    # print(client.executeAction(actions), file=sys.stderr, flush=True)

    agt1 = Agent('0', (5,3), Atom("BoxAt",["B1", (5,1)]), [Move, Push, Pull], "green")
    agt0 = Agent('1', (1,8), Atom("BoxAt",["B1", (1,4)]), [Move, Push, Pull], "red")
    currentState = client.initial_state

    print("Begin", file=sys.stderr, flush=True)
    # action_agt1 = agt1.getPossibleActions(currentState)
    # print(action_agt1, file=sys.stderr, flush=True)

    # while True:
    #     # print(currentState, file=sys.stderr, flush=True)
    #     action_agt1 = agt1.getPossibleActions(currentState)
    #     action_agt0 = agt0.getPossibleActions(currentState)
    #
    #     action_agt0 = action_agt0[np.random.choice(len(action_agt0))]
    #     action_agt1 = action_agt1[np.random.choice(len(action_agt1))]
    #     # print(action_agt0, action_agt1, file=sys.stderr, flush=True)
    #
    #     joint_action = [action_agt0[2],action_agt1[2]]
    #     print(joint_action, file=sys.stderr, flush=True)
    #     valid = client.executeAction([joint_action])
    #     # print(valid, file=sys.stderr, flush=True)
    #     if valid[0][0] == 'true' and valid[0][1] == 'true':
    #         action_agt0[0].execute(currentState, action_agt0[1])
    #         action_agt1[0].execute(currentState, action_agt1[1])
    #
    #         # agt0.position = action_agt0[3]
    #         # agt1.position = action_agt1[3]
    #     else:
    #         break

    agt1.plan(currentState)
    print(agt1.current_plan, file=sys.stderr, flush=True)



if __name__ == '__main__':
    # Run client.
    main()
