import argparse
import re
import sys
import numpy as np

from state import State
from atom import Atom
from agent import Agent
from action import *
from knowledgeBase import KnowledgeBase

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
            atoms = KnowledgeBase("Atoms")
            rigidAtoms = KnowledgeBase("Rigid atoms")
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
                    IsColor = Atom('IsColor', color)
                    rigidAtoms.update(IsColor)

                    objects = splittedLine[1].split(",")
                    for obj in objects:
                        boxColors[obj.replace(' ', '')] = color

                if initial:
                    for col, char in enumerate(line):
                        if char == '+':
                            a=1
                        elif char in "0123456789":
                            AgentAt = Atom('AgentAt', char, (row, col))
                            atoms.update(AgentAt)

                            Color = Atom('Color', char, boxColors[char])
                            rigidAtoms.update(Color)

                        elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                            Box = 'B' + str(currentBox)

                            Color = Atom('Color', Box, boxColors[char])
                            rigidAtoms.update(Color)

                            Letter = Atom('Letter', Box, char)
                            rigidAtoms.update(Letter)

                            BoxAt = Atom('BoxAt', Box, (row, col))
                            atoms.update(BoxAt)

                            currentBox += 1
                        elif char == ' ':
                            # Free cell.
                            FreeL = Atom('Free', (row, col))
                            atoms.update(FreeL)
                            pass
                        else:
                            print('Error, read invalid level character: {}'.format(char), file=sys.stderr, flush=True)
                            sys.exit(1)

                        if char != '+':
                            if row > 0 and col < len(previousLine):
                                if previousLine[col] != '+':
                                    rigidAtoms.update(Atom('Neighbour', (row - 1, col), (row, col)))
                                    rigidAtoms.update(Atom('Neighbour', (row, col), (row - 1, col)))
                            if col > 0:
                                if line[col - 1] != '+':
                                    rigidAtoms.update(Atom('Neighbour', (row, col), (row, col - 1)))
                                    rigidAtoms.update(Atom('Neighbour', (row, col - 1), (row, col)))


                    row += 1

                if goal:
                    for col, char in enumerate(line):
                        if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                            Goal = 'G' + str(currentGoal)

                            Letter = Atom('Letter', Goal, char.lower())
                            rigidAtoms.update(Letter)

                            GoalAt = Atom('GoalAt', Goal, (row, col))
                            rigidAtoms.update(GoalAt)

                            currentGoal += 1

                    row += 1

                previousLine = line
                line = server_messages.readline().rstrip()



            self.initial_state = State('s0', atoms, rigidAtoms)


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
