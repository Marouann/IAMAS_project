import sys, time
from state import State
from atom import Atom, StaticAtom, DynamicAtom
from knowledgeBase import KnowledgeBase
from heapq import heapify, heappush, heappop
from multiprocessing import Process, Manager
import numpy as np

STATUS_WAIT_REPLAN = 0
STATUS_REPLAN_AFTER_CONFLICT = 1
STATUS_REPLAN_NO_PLAN_FOUND = 2
STATUS_REPLAN_GHOST = 3
STATUS_SOLVING_CONFLICT = 4
STATUS_DEADLOCK = 5
STATUS_NOT_REPLAN = 6


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
    clusters = {}
    added_to_a_cluster = set()
    for r in range(row):
        for c in range(col):
            r_c_already_in_a_cluster = (r, c) in added_to_a_cluster

            if not r_c_already_in_a_cluster:
                clusters[str((r, c))] = set()
                clusters[str((r, c))].add((r, c))
                added_to_a_cluster.add((r, c))

            for distance, cell in distance_calculator((r, c)):
                cell_already_in_a_cluster = cell in added_to_a_cluster

                if not cell_already_in_a_cluster:
                    clusters[str((r, c))].add(cell)
                    added_to_a_cluster.add(cell)

                atom = StaticAtom('Distance', (r, c), cell)
                atom.assign_property(distance)
                adjacency.update(atom)

            if not r_c_already_in_a_cluster and len(clusters[str((r, c))]) == 1:
                del clusters[str((r, c))]

    print('Distances computed in %.2f seconds' % (time.time() - start_time), file=sys.stderr, flush=True)

    # print('I calculated {} distances'.format(adjacency), file=sys.stderr, flush=True)
    return {'distances': adjacency, 'clusters': clusters}

def replace_box_by_walls(state: 'State', clusters, boxes, agents):
    cluster_colors = {}
    for cluster_name in clusters:
        cluster_colors[cluster_name] = set()

    for agent in agents:
        for cluster_name, cluster in clusters.items():
            if agent['initial_position'] in cluster:
                cluster_colors[cluster_name].add(agent['color'])
                continue

    for box in boxes:
        for cluster_name, cluster in clusters.items():
            if box['initial_position'] in cluster:
                if not box['color'] in cluster_colors[cluster_name]:
                    (row, col) = box['initial_position']
                    state.atoms.delete(DynamicAtom('BoxAt^', box['initial_position'], box['name']))
                    for (i, j) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        state.rigid_atoms.delete(Atom('Neighbour', (row, col), (row + i, col + j)))
                        state.rigid_atoms.delete(Atom('Neighbour', (row + i, col + j), (row, col)))

                    for cell in cluster:
                        state.rigid_atoms.delete(StaticAtom('Distance', (row, col), cell))
                        state.rigid_atoms.delete(StaticAtom('Distance', cell, (row, col)))
                continue

    return state


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
        agent_goals = []
        boxes = []

        currentBox = 1
        currentGoal = 1
        currentAgentGoal = 1

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

                        AgentAt = DynamicAtom('AgentAt^', (row, col), char)
                        AgentAt.assign_property((row, col))
                        atoms.update(AgentAt)

                        Color = Atom('Color', char, boxColors[char])
                        rigidAtoms.update(Color)

                        Color = StaticAtom('Color*', char)
                        Color.assign_property(boxColors[char])
                        rigidAtoms.update(Color)

                        agents.append({'name': char, 'color': boxColors[char], 'initial_position': (row, col)})

                    elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                        Box = 'B' + str(currentBox)

                        Color = Atom('Color', Box, boxColors[char])
                        rigidAtoms.update(Color)

                        Color = StaticAtom('Color*', Box)
                        Color.assign_property(boxColors[char])
                        rigidAtoms.update(Color)

                        Letter = Atom('Letter', Box, char)
                        rigidAtoms.update(Letter)

                        Letter = StaticAtom('Letter*', Box)
                        Letter.assign_property(char)
                        rigidAtoms.update(Letter)

                        BoxAt = Atom('BoxAt', Box, (row, col))
                        atoms.update(BoxAt)

                        BoxAt = DynamicAtom('BoxAt^', (row, col), Box)
                        BoxAt.assign_property((row, col))
                        atoms.update(BoxAt)

                        boxes.append({'name': Box, 'letter': char, 'color': boxColors[char], 'initial_position': (row, col)})

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

                    if char in "0123456789":
                        AgentGoal = 'AG' + str(currentAgentGoal)

                        Letter = Atom('Letter', AgentGoal, char)
                        rigidAtoms.update(Letter)

                        AgentGoalAt = Atom('AgentGoalAt', AgentGoal, (row, col))
                        rigidAtoms.update(AgentGoalAt)

                        agent_goals.append({'name': AgentGoal, 'position': (row, col), 'letter': char})

                        currentAgentGoal += 1

                row += 1

            previousLine = line
            line = server_messages.readline().rstrip()


    except Exception as ex:
        print('Error parsing level: {}.'.format(repr(ex)), file=sys.stderr, flush=True)
        sys.exit(1)

    return {
        'initial_state': State('s0', goals, agent_goals, atoms, rigidAtoms),
        'domain': domain,
        'levelName': levelName,
        'agents': agents,
        'goals': goals,
        'agent_goals': agent_goals,
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


def areGoalsMet(state: 'State', goals) -> 'bool':
    for goal in goals:
        if goal not in state.atoms:
            return False
    return True


def areAgentGoalsMet(state: 'State', agent_goals) -> 'bool':
    for goal in agent_goals:
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
    result = { 'safe': [], 'tunnel': [] }
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
                result['safe'].append((row, col))
                continue

            if safe_cells[1] == [True, True, True] and safe_cells[2] == [True, True, True]:
                result['safe'].append((row, col))
                continue

            if [row[0] for row in safe_cells] == [True, True, True] and [row[1] for row in safe_cells] == [True, True, True]:
                result['safe'].append((row, col))
                continue

            if [row[1] for row in safe_cells] == [True, True, True] and [row[2] for row in safe_cells] == [True, True, True]:
                result['safe'].append((row, col))
                continue

            #add corners as free cells
            if list(np.array(safe_cells).reshape(-1)) == [True, True, False, True, True, False, False, False, False]:
                result['safe'].append((row, col))
                continue

            if list(np.array(safe_cells).reshape(-1)) == [False,True, True, False, True, True, False, False, False]:
                result['safe'].append((row, col))
                continue

            if list(np.array(safe_cells).reshape(-1)) == [False, False, False, False, True, True, False, True, True]:
                result['safe'].append((row, col))
                continue

            if list(np.array(safe_cells).reshape(-1)) == [False, False, False, True, True, False, True, True, False]:
                result['safe'].append((row, col))
                continue

            # We then check if the cell is a tunel
            if [safe_cells[0][1], safe_cells[2][1], safe_cells[1][0], safe_cells[1][2]] == [False, False, True, True]:
                result['tunnel'].append((row, col))
                continue

            if [safe_cells[0][1], safe_cells[2][1], safe_cells[1][0], safe_cells[1][2]] == [True, True, False, False]:
                result['tunnel'].append((row, col))
                continue



    for safe_cell in result['safe']:
        for tunnel_cell in result['tunnel']:
            if Atom('Neighbour', safe_cell, tunnel_cell) in state.rigid_atoms and safe_cell in result['safe']:
                result['safe'].remove(safe_cell)

    return result

def updateSafeCells(state, cells):
    freeSafeCells = []
    for cell in cells:
        if not state.find_object_at_position(cell[1]):
            freeSafeCells.append(cell)

    return freeSafeCells
