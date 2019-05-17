import sys, time
from state import State
from atom import Atom, DynamicAtom
from knowledgeBase import KnowledgeBase
from heapq import heapify, heappush, heappop
from multiprocessing import Process, Manager

STATUS_WAIT_REPLAN = 0
STATUS_REPLAN_AFTER_CONFLICT = 1
STATUS_REPLAN_NO_PLAN_FOUND = 2
STATUS_REPLAN_GHOST = 3

def level_adjacency(state: 'State', row=60, col=60) -> 'KnowledgeBase':
    '''Calculates real distances between cells in a level'''

    def distance_calculator(coord: ('int', 'int')):
        frontier = list()
        explored = set()
        memory = list()
        explored.add(coord)  ## so we do not calculate the distance between itself
        if state.find_neighbours(coord):
            for neighbour in state.find_neighbours(coord):
                heappush(frontier, (1, neighbour))
                explored.add(neighbour)
                memory.append((1, neighbour))

        while frontier:
            current = heappop(frontier)
            if state.find_neighbours(current[1]):
                for neighbour in state.find_neighbours(current[1]):
                    if neighbour not in explored:
                        memory.append((current[0] + 1, neighbour))
                        explored.add(neighbour)
                        heappush(frontier, (current[0] + 1, neighbour))
                heapify(frontier)
        memory.append((0, coord))
        return memory

    start_time = time.time()
    adjacency = KnowledgeBase('Real Distances')
    for r in range(row):
        for c in range(col):
            for distance, cell in distance_calculator((r, c)):
                atom = DynamicAtom('Distance', (r, c), cell)
                atom.assign_property(distance)
                adjacency.update(atom)

    print('Distances computed in %.2f seconds' %(time.time() - start_time), file=sys.stderr, flush=True)

    # print('I calculated {} distances'.format(adjacency), file=sys.stderr, flush=True)
    return adjacency

def get_level(server_messages):
    initial_state = None
    domain = None
    levelName = None

    max_row = 0
    max_col = 0

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
                domain = line
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
                max_row = max(row, max_row)
                for col, char in enumerate(line):
                    max_col = max(col, max_col)
                    if char == '+':
                        a = 1
                    elif char in "0123456789":
                        AgentAt = Atom('AgentAt', char, (row, col))
                        atoms.update(AgentAt)

                        AgentAt = DynamicAtom('AgentAt*', char)
                        AgentAt.assign_property((row,col))
                        atoms.update(AgentAt)

                        Color = Atom('Color', char, boxColors[char])
                        rigidAtoms.update(Color)

                        Color = DynamicAtom('Color*', char)
                        Color.assign_property(boxColors[char])
                        rigidAtoms.update(Color)

                        agents.append({'name': char, 'color': boxColors[char]})

                    elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                        Box = 'B' + str(currentBox)

                        Color = Atom('Color', Box, boxColors[char])
                        rigidAtoms.update(Color)

                        Color = DynamicAtom('Color*', Box)
                        Color.assign_property(boxColors[char])
                        rigidAtoms.update(Color)

                        Letter = Atom('Letter', Box, char)
                        rigidAtoms.update(Letter)

                        Letter = DynamicAtom('Letter*', Box)
                        Letter.assign_property(char)
                        rigidAtoms.update(Letter)

                        BoxAt = Atom('BoxAt', Box, (row, col))
                        atoms.update(BoxAt)

                        BoxAt = DynamicAtom('BoxAt*', Box)
                        BoxAt.assign_property((row,col))
                        atoms.update(BoxAt)

                        boxes.append({'name': Box, 'letter': char, 'color': boxColors[char]})

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

                        goals.append({'name': Goal, 'position': (row, col), 'letter': char})

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
        'boxes': boxes,
        'rows': max_row,
        'cols': max_col,
    }

def isAllExecuted(answer):
    isExecuted = True
    for bool in answer:
        if bool == "false":
            isExecuted = False
    return isExecuted

def areGoalsMet(state: 'State', goals)-> 'bool':
    for goal in goals:
        if goal not in state.atoms:
            return False
    return True

def get_cluster_conflict(who_is_conflicting_with, key_to_remove):
    clusters = []
    all_agents = who_is_conflicting_with.keys()
    for agent in all_agents:
        cluster = find_cluster_of_agent(agent, clusters)
        if cluster is not False:
            for conflicting_agent in who_is_conflicting_with[agent]:
                if conflicting_agent['status'] == 'blocked' and conflicting_agent['agent'] not in key_to_remove:
                    cluster.add(conflicting_agent['agent'])
        else:
            cluster = set()
            if agent not in key_to_remove:
                cluster.add(agent)
                for conflicting_agent in who_is_conflicting_with[agent]:
                    if conflicting_agent['status'] == 'blocked' and conflicting_agent['agent'] not in key_to_remove:
                        cluster.add(conflicting_agent['agent'])
                clusters.append(cluster)
    return clusters

def find_cluster_of_agent(agent, clusters):
    for cluster in clusters:
        if agent in cluster:
            return cluster
    return False


def is_safe_cell(state, row, col, i, j):
    is_goal = False
    for goal in state.goals:
        if goal['position'] == (row + i, col + j):
            is_goal = True
            break;

    return Atom('Neighbour', (row, col), (row + i, col + j)) in state.rigid_atoms and not is_goal

def identify_cells(state, rows, cols):
    rigid_atoms_to_add = []
    for row in range(rows + 1):
        for col in range(cols + 1):
            # We check the neighbours
            safe_cells = [[False for k in range(3)] for l in range(3)]
            for i in range(3):
                for j in range(3):
                    if i == 1 or j == 1:
                        safe_cells[i][j] = is_safe_cell(state, row, col, i - 1, j - 1)
            
            safe_cells[0][0] = safe_cells[1][0] and is_safe_cell(state, row, col - 1, -1, 0) or safe_cells[0][1] and is_safe_cell(state, row - 1, col, 0, -1)
            safe_cells[2][0] = safe_cells[1][0] and is_safe_cell(state, row, col - 1, 1, 0) or safe_cells[2][1] and is_safe_cell(state, row + 1, col, 0, -1)
            safe_cells[0][2] = safe_cells[1][2] and is_safe_cell(state, row, col + 1, 0, -1) or safe_cells[0][1] and is_safe_cell(state, row - 1, col, 0, 1)
            safe_cells[2][2] = safe_cells[1][2] and is_safe_cell(state, row, col + 1, 0, 1) or safe_cells[2][1] and is_safe_cell(state, row + 1, col, 0, 1)

            safe_cells[1][1] = True

            # We first check if the cell is safe
            if safe_cells[0] == [True, True, True] and safe_cells[1] == [True, True, True]:
                rigid_atoms_to_add.append(Atom('Safe', (row, col)))
                continue

            if safe_cells[1] == [True, True, True] and safe_cells[2] == [True, True, True]:
                rigid_atoms_to_add.append(Atom('Safe', (row, col)))
                continue

            if [row[0] for row in safe_cells] == [True, True, True] and [row[1] for row in safe_cells] == [True, True, True]:
                rigid_atoms_to_add.append(Atom('Safe', (row, col)))
                continue

            if [row[1] for row in safe_cells] == [True, True, True] and [row[2] for row in safe_cells] == [True, True, True]:
                rigid_atoms_to_add.append(Atom('Safe', (row, col)))
                continue
            
            # We then check if the cell is a tunel
            if [safe_cells[0][1], safe_cells[2][1], safe_cells[1][0], safe_cells[1][2]] == [False, False, True, True]:
                rigid_atoms_to_add.append(Atom('Tunnel', (row, col)))
                continue
            
            if [safe_cells[0][1], safe_cells[2][1], safe_cells[1][0], safe_cells[1][2]] == [True, True, False, False]:
                rigid_atoms_to_add.append(Atom('Tunnel', (row, col)))
                continue

    print([str(atom) for atom in rigid_atoms_to_add], file=sys.stderr)
