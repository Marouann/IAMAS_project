
import sys

from state import State
from atom import Atom
from knowledgeBase import KnowledgeBase

def getLevel(server_messages):
    initial_state = None
    domain = None
    levelName = None

    try:
        line = server_messages.readline()
        color = False
        initial = False
        goal = False
        row = 0
        previousLine = line

        # Initialize the predicates
        atoms = KnowledgeBase("Atoms")
        rigidAtoms = KnowledgeBase("Rigid atoms")
        boxColors = {}

        agents = []
        goals = []
        boxes = []

        currentBox = 1
        currentGoal = 1

        while line != "#end":
            if line == '#domain':
                line = server_messages.readline().rstrip()
                domain= line
            elif line == "#levelname":
                line = server_messages.readline().rstrip()
                levelName = line
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
                line = server_messages.readline().rstrip()
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

                        agents.append({ 'name': char, 'color': boxColors[char] })

                    elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                        Box = 'B' + str(currentBox)

                        Color = Atom('Color', Box, boxColors[char])
                        rigidAtoms.update(Color)

                        Letter = Atom('Letter', Box, char)
                        rigidAtoms.update(Letter)

                        BoxAt = Atom('BoxAt', Box, (row, col))
                        atoms.update(BoxAt)

                        boxes.append({ 'name': Box, 'letter': char, 'color': boxColors[char]})

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

                        Letter = Atom('Letter', Goal, char)
                        rigidAtoms.update(Letter)

                        GoalAt = Atom('GoalAt', Goal, (row, col))
                        rigidAtoms.update(GoalAt)

                        goals.append({ 'name': Goal, 'position': (row, col), 'letter': char })

                        currentGoal += 1

                row += 1

            previousLine = line
            line = server_messages.readline().rstrip()

    except Exception as ex:
        print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
        sys.exit(1)

    return {
            'initial_state': State('s0', goals, atoms, rigidAtoms),
            'domain': domain,
            'levelName': levelName, 
            'agents': agents,
            'goals': goals,
            'boxes': boxes
        }
