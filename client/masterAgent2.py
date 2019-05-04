import argparse
import re
import sys
import numpy as np
#from collections import deque

from state import State
from atom import Atom
from agent import *
from action import *
from knowledgeBase import KnowledgeBase
from utils import *


class MasterAgent:
    def __init__(self, initial_state: 'State', agents: '[Agent]', boxes: '[dict]'):
        self.currentState = initial_state

        self.agents = []
        self.boxes = boxes  # List of { 'name': Box, 'letter': char, 'color': color }
        self.goalsInAction = []

        for agt in sorted(agents, key=lambda k: k['name']):
            agtAt = initial_state.find_agent(agt['name'])
            agent = Agent(agt['name'], agtAt, None, [Move, Push, Pull, NoOp], agt['color'])
            self.agents.append(agent)

    def prioritizeGoals(self, goals):
        # Sort goals 1st by number of free neighbour fields, then by number of neighbour goals)
        sortedGoals = sorted(goals,
                                key=lambda x: (self.currentState.getNeithbourFieldsWithoutGoals(x["position"]).__len__(),
                                self.currentState.getNeithbourGoals(x["position"]).__len__()))

        return sortedGoals

    def assignGoals(self, agentsToReplan):
        (goalsToAssign, goalsMet) = self.currentState.get_unmet_goals()
        if agentsToReplan != []:
            print('\nFree agents : ' + str([agent.name for agent in agentsToReplan]), file=sys.stderr, flush=True)
            print('Goals unmet : ' + str(goalsToAssign), file=sys.stderr, flush=True)
            print('Goals already met : ' + str(goalsMet), file=sys.stderr, flush=True)

        boxesHandled = []
        # Boxes already placed on the goal
        for goal in goalsMet:
            boxOnGoal = self.currentState.find_box(goal['position'])
            boxesHandled.append(boxOnGoal.variables[0])

        # Boxes that are currently handled by agents
        for agent in self.agents:
            if agent.goal is not None:
                boxesHandled.append(agent.goal.variables[0])

        # Each agent that is passed to assignGoals either finished doing its job, or it's his 1st one
        # Hence we if self.goalsInAction contains agent.goal this job has been finished so we need to remove it
        for agent in agentsToReplan:
            if agent.goal_details in self.goalsInAction:
                self.goalsInAction.remove(agent.goal_details)

        for goal in self.goalsInAction:
            if goal in goalsToAssign:
                goalsToAssign.remove(goal)

        prioritizedGoals = self.prioritizeGoals(goalsToAssign)
        # print(prioritizedGoals, file=sys.stderr)
        if prioritizedGoals != []:
            for agent in agentsToReplan:
                if agent.current_plan != []:

                    print(agent.name, agent.current_plan[0], file=sys.stderr, flush=True)
                else:
                    print('Agent', agent.name, 'has no plan!', file=sys.stderr, flush=True)
                # print(agent.occupied, file=sys.stderr)
                if agent.occupied == False:
                    print('Agent', agent.name, 'is not occupied!', file=sys.stderr, flush=True)
                    for goal in prioritizedGoals:
                        if agent.goal is not None:
                            # print('Agent already has a goal, continue: ' + str(goal), file=sys.stderr, flush=True)
                            continue
                        if goal in self.goalsInAction:
                            # print('Goal has already been assigned : ' + str(goal), file=sys.stderr, flush=True)
                            continue

                        possibleBoxes = []
                        for box in self.boxes:
                            if box['color'] == agent.color and \
                                    box['letter'] == goal['letter'] and \
                                    box['name'] not in boxesHandled:
                                possibleBoxes.append(box)

                        prioritizedBoxes = sorted (possibleBoxes,
                                                   key=lambda x: self.currentState.find_box_goal_distance(x["name"], goal))
                        goalNotAssigned = True
                        while goalNotAssigned and prioritizedBoxes != []:
                            box = prioritizedBoxes.pop(0)
                            boxAlreadyPlaced = False
                            for goalmet in goalsMet:
                                boxPlaced = self.currentState.find_box(goalmet['position'])
                                if boxPlaced.variables[0] == box['name']:
                                    boxAlreadyPlaced = True

                            if not boxAlreadyPlaced:
                                agent.assignGoal(Atom("BoxAt", box['name'], goal['position']), goal)
                                self.goalsInAction.append(goal)
                                boxesHandled.append(box['name'])
                                goalNotAssigned = False
                                if not agent.goal in self.currentState.atoms:
                                    agent.plan(self.currentState)
                                    if agent.current_plan == []:
                                        agent.status = STATUS_REPLAN_NO_PLAN_FOUND

        for agent in agentsToReplan:
            print('agent: ' + str(agent.name) + ', has goal: ' + str(agent.goal), file=sys.stderr, flush=True)

    def solveLevel(self):
        # We need to check the goal.
        self.assignGoals(self.agents)

        # Store previous and current joint actions
        previous_action = [[],[], []]
        for agt_index in range(len(self.agents)):
            action = {'action': NoOp, 'params': [str(agt_index), self.currentState.find_agent(str(agt_index))],
                                    'message':'NoOp',
                                    'priority':4}

            '''
            We want to keep the last to actions for conflict management, previous_action needs to be initialized with length 2
            '''
            previous_action[0].append(action)    # [ pop(0) <-[Previous joint action], [Current joint action] <- append(jointaction)]
            previous_action[1].append(action)
            previous_action[2].append(action)

        # counter in while
        nb_iter = 0

        # remember if last action has been successful because during conflict solving action are performed successfuly
        # even if the conflict is not totally solved
        old_valids = [False,False, False]
        # stop util reached goal
        while self.currentState.get_unmet_goals()[0] != []:
            # print(self.currentState.get_unmet_goals()[0], file=sys.stderr)
            nb_iter += 1

            # First we loop over agent to free them if their goal are met
            self.assignGoals([agent for agent in self.agents if agent.occupied == False])

            # Gets the first actions from each agent (joint action on first row)
            actions_to_execute = self.getNextJointAction()

            # update previous joint action
            previous_action.append(actions_to_execute)
            previous_action.pop(0)

            # Keep the response from the server ([true, false, ...])

            old_valids.pop(0)
            valid = self.executeAction(actions_to_execute)
            old_valids.append(reduceServerAnswer(valid))

            # 'agents_with_conflit': List of agents which cannot execute their actions (e.g [agt0, agt1, agt6])
            agents_with_conflit = [i for i in range(len(valid)) if valid[i]=='false']

            # If 'agents_with_conflit' not empty then solve conflict
            if agents_with_conflit != []:
                self.solveConflict(agents_with_conflit, previous_action)
                # self.solveConflict(agents_with_conflit,actions_to_execute, previous_action)

            for agent in self.agents:
                print('Agents', agent.name, file=sys.stderr)
                print(agent.status, file=sys.stderr)
                print(agent.goal, file=sys.stderr)
                print(agent.goal_details, file=sys.stderr)

            print(old_valids, file=sys.stderr)
            if False not in old_valids:
                self.replanAgentWithStatus(STATUS_REPLAN_AFTER_CONFLICT)

            # Replan for agents that have goals but no plan (i.e. status "W")
            self.replanAgentWithStatus(STATUS_WAIT_REPLAN)

            if nb_iter % 5 == 0:
                self.replanAgentWithStatus(STATUS_REPLAN_NO_PLAN_FOUND)

            if nb_iter > 100:
                break


    def replanAgentWithStatus(self, status:'Int'):
        for agent in self.agents:
            if agent.status == status:
                print('Replanning with status', agent.status, file=sys.stderr)
                agent.plan(self.currentState)
                if agent.current_plan != []:
                    agent.status = None
                    agent.occupied = False
                    agent.goal = None

    def getNextJointAction(self):
        # initialize joint_action with 'NoOp' of length number of agents ['NoOp', 'NoOp', 'NoOp', ...]
        joint_action = []
        for agent in self.agents:
            # If there are still actions in current plan pop the first action and
            if agent.current_plan != []:
                # print(agent.current_plan, file=sys.stderr)
                joint_action.append(agent.current_plan.pop(0))
            else:
                joint_action.append({'action': NoOp,
                                            'params': [agent.name, self.currentState.find_agent(agent.name)],
                                            'message':'NoOp',
                                            'priority':4})

        return joint_action

    def executeAction(self, jointAction, multi_goal=False):
        server_answer = ''
        actions_string = ''

        for agent_action in jointAction:
            actions_string += agent_action['message']
            actions_string += ';'

        actions_string = actions_string[:-1]  # remove last ';' from the string
        print(actions_string, file=sys.stderr, flush=True)  # print out

        # retrieve answer from server and separate answer for specific action
        # [:-1] is only to remove the '\n' at the end of response
        print(actions_string, flush=True)  # send to server
        server_answer = sys.stdin.readline()[:-1].split(";")

        print('Server response : ' + str(server_answer), file=sys.stderr, flush=True)

        for i, answer in enumerate(server_answer):
            if answer == 'true':
                jointAction[i]['action'].execute(self.currentState, jointAction[i]['params'])

        if not multi_goal:
            for agent in self.agents:
                if agent.goal in self.currentState.atoms:
                    print("Goal", agent.goal, file=sys.stderr)
                    agent.occupied = False
                    agent.current_plan = []
                    agent.goal = None

        return server_answer

    def solveConflict(self, agents_with_conflict, previous_actions):
        print('Conflict found', file=sys.stderr)
        remaining_agents_with_conflict = list(agents_with_conflict)
        # First we check if now the action is applicable:
        # Conflict type 1.
        for i in agents_with_conflict:
            action = previous_actions[2][i]
            if action['action'].checkPreconditions(self.currentState, action['params']):
                # if the action is applicable, we apply it while stopping the others agents.
                jointAction = [{'action': NoOp, 'params': [str(agt_index), self.currentState.find_agent(str(agt_index))],
                                    'message':'NoOp',
                                    'priority':4} for agt_index in range(len(self.agents))]
                jointAction[i] = action
                remaining_agents_with_conflict.remove(i)
                self.executeAction(jointAction)

        who_is_conflicting_with = {}
        for current_agent_index in remaining_agents_with_conflict:
            who_is_conflicting_with[current_agent_index] = []

            '''
             If the agent can not apply its action there is two case possible:
             - The agent is conflicting alone, he wants to go on an occupied cell. But the "blocker" can continue its way without conflicting
                   => We can make the agent wait or ask for help if the blocker does not plan to move.
             - Two agents are trying to go on the same way
                   => We need to prioritize someone.

             First we need to know what is blocking
             To do so, we need to check the unmet preconditions
            '''

            action = previous_actions[2][current_agent_index]
            preconds = action['action'].preconditions(*action['params'])
            unmet_preconds = []
            for atom in preconds:
                if atom not in self.currentState.atoms and atom not in self.currentState.rigid_atoms:
                    unmet_preconds.append(atom)

            # Now we want to know which agent has unmet this precondition
            for other_agent in [agt for agt in self.agents if int(agt.name) != current_agent_index]:
                other_agent_index = int(other_agent.name)
                # We check if the other_agent was able to performs its action
                if other_agent_index in remaining_agents_with_conflict:
                    '''
                    Conflict type 4:
                    More than one agent did not perform their last actions
                    --> We need to look at actions executed one step before to find the origin of the conflict, i.e in previous_action
                    '''
                    print('More than one conflicting agent', file=sys.stderr)

                    other_action = previous_actions[1][other_agent_index]
                    neg_effects = other_action['action'].negative_effects(*other_action['params'])


                    other_agent_is_the_problem = False
                    unmet_precond_due_to_other_agent = None
                    for atom in unmet_preconds:
                        if atom in neg_effects:
                            other_agent_is_the_problem = True
                            unmet_precond_due_to_other_agent = atom

                    if other_agent_is_the_problem:
                        if other_action['message'] != 'NoOp':
                            who_is_conflicting_with[current_agent_index].append({
                                'agent': other_agent_index,
                                'status': 'blocked', # blacked ?
                                'success': False,
                                'unmet_precond': unmet_precond_due_to_other_agent,
                                'priority': len(self.agents[current_agent_index].current_plan)
                            })

                else:
                    other_agent_is_the_problem = False
                    unmet_precond_due_to_other_agent = None
                    last_action = previous_actions[2][other_agent_index]
                    for previous_action in reversed(previous_actions):
                        if not other_agent_is_the_problem:
                            for atom in unmet_preconds:
                                other_action = previous_action[other_agent_index]
                                print(other_action, file=sys.stderr)
                                neg_effects = other_action['action'].negative_effects(*other_action['params'])
                                if atom in neg_effects:
                                    other_agent_is_the_problem = True
                                    unmet_precond_due_to_other_agent = atom

                    # If the agent is the problem, we have to store that it is conflicting with current_agent_index
                    if other_agent_is_the_problem:
                        if last_action['message'] != 'NoOp':
                            who_is_conflicting_with[current_agent_index].append({
                                'agent': other_agent_index,
                                'status': 'moving',
                                'success': True,
                                'unmet_precond': unmet_precond_due_to_other_agent
                            })
                        else:
                            who_is_conflicting_with[current_agent_index].append({
                                'agent': other_agent_index,
                                'status': 'waiting',
                                'success': True,
                                'unmet_precond': unmet_precond_due_to_other_agent
                            })

        prioritization_needed = False

        for current_agent_index, conflicting_agents in who_is_conflicting_with.items():
            # Now we know, who is conflicting, and what are they doing.
            # We can resolve the conflict
            conflicting_agents = who_is_conflicting_with[current_agent_index]
            # First, if there is only one agent that is conflicting:

            print("Conclicting agents", conflicting_agents, file=sys.stderr)

            if len(conflicting_agents) == 1:
                conflicting_agent = conflicting_agents[0]
                # We check if we're in the case where the blocking agent can continue his plan
                if conflicting_agent['success']:
                    # If this agent is successful and moving we will wait.
                    # Conflict Type 2
                    if conflicting_agent['status'] == 'moving':
                        self.agents[current_agent_index].current_plan.insert(0, previous_actions[2][current_agent_index])
                        self.agents[current_agent_index].current_plan.insert(0, {
                            'action': NoOp,
                            'params': [str(current_agent_index), self.currentState.find_agent(str(current_agent_index))],
                            'message':'NoOp',
                            'priority':4,
                        })
                    # If the agent is not moving, we free the agent to let him plan for a new goal
                    # Conflit type 3
                    else:

                        self.agents[current_agent_index].current_plan.insert(0, previous_actions[2][current_agent_index])
                        self.executeConflictSolution(self.agents[conflicting_agent['agent']],
                                                    conflicting_agent['unmet_precond'],
                                                    list(who_is_conflicting_with.keys()))
                        # self.agents[conflicting_agent['agent']].status = STATUS_WAIT_REPLAN # We could free him totally.

                else:
                    prioritization_needed = True
                    pass # need to define some priority between agents

        if prioritization_needed:
            print("Prioritization needed", file=sys.stderr)

            # first retrieve agent that has the smallest plan
            conflicting_agent_index = max(who_is_conflicting_with.keys(),
                                            key=lambda key: who_is_conflicting_with[key][0]['priority'])
            conflict_solution = conflicting_agent['unmet_precond']

            for agent in self.agents:
                agent.current_plan.insert(0, previous_actions[2][int(agent.name)])
            self.executeConflictSolution(self.agents[conflicting_agent_index],
                                        conflict_solution,
                                        list(who_is_conflicting_with.keys()))


    '''
    This function store the goal of an agent while he executes the solution of a conflict
    '''
    def executeConflictSolution(self, agent:'Agent', solution:'Atom', conflicting_with = None):
        goal_keep = agent.goal
        goal_details_keep = agent.goal_details
        agent.current_plan = []
        agent.occupied = True
        agent.goal = solution
        agent.goal_details = None

        agent.plan(self.currentState, strategy="bfs")
        for other_agent in self.agents:
            if other_agent.name != agent.name:
                self.agents[int(other_agent.name)].current_plan.insert(0,{
                    'action': NoOp,
                    'params': [other_agent.name, self.currentState.find_agent(other_agent.name)],
                    'message':'NoOp',
                    'priority':4,
                })
        print('\n\n\n\nplan length', agent.current_plan, file=sys.stderr)
        if len(agent.current_plan) == 0:
            # Conflict type 5: conflict solver is blocked need to reverse priority.
            # in that case, we ask for help by adding new goals
            print("Conflict solver is blocked, need help", file=sys.stderr)
            print(conflicting_with, file=sys.stderr)
            agent.occupied = False
            agent.status = None

            # at this point we stop keeping in memory information of the previous goal
            # we will need to fully replan after the conflict is solved.
            self.goalsInAction.remove(goal_details_keep)
            for agent_index in conflicting_with:
                self.agents[agent_index].occupied = False
                self.agents[agent_index].status = None

            available_agents = [agent for agent in self.agents if agent.occupied == False]
            print('Available agents are', available_agents, file=sys.stderr)
            self.reverse_conflict(available_agents)
        else:
            agent.goal = goal_keep
            agent.goal_details = goal_details_keep
            agent.status = STATUS_REPLAN_AFTER_CONFLICT

    def reverse_conflict(self, available_agents):
        self.currentState.helping_goals = self.getHelpingGoals(available_agents)

        while not areGoalsMet(self.currentState, self.currentState.helping_goals):
            print("Helping goal:", file=sys.stderr)
            for goal in self.currentState.helping_goals:
                print(goal, file=sys.stderr)
            responsible = {} # dict used to divide goals between different agents
            for agent in available_agents:
                responsible[agent.name] = []

            for goal in self.currentState.helping_goals:
                obstructed_by = self.currentState.find_object_at_position(goal.variables[0])

                if obstructed_by is not False and obstructed_by.name == 'AgentAt':
                    responsible[obstructed_by.variables[0]].append(goal)

                elif obstructed_by is not False and obstructed_by.name == 'BoxAt':
                    print("A box is on the way", file=sys.stderr)
                    closest_agent = None
                    min_distance = np.inf
                    problematic_box = list(filter(lambda box: box['name'] == obstructed_by.variables[0], self.boxes))[0]
                    for agent in available_agents:
                        if agent.color == problematic_box['color']:
                            dist_ = self.currentState.find_distance(self.currentState.find_agent(agent.name),
                                                                    self.currentState.find_box_position(problematic_box['name']))
                            if dist_ < min_distance:
                                min_distance = dist_
                                closest_agent = agent
                    if closest_agent is not None:
                        responsible[closest_agent.name].append(goal)
                else:
                    for agent in available_agents:
                        responsible[agent.name].append(goal)
            print("goal division:", responsible, file=sys.stderr)
            for name, goals in responsible.items():
                self.agents[int(name)].goal = goals
                self.agents[int(name)].plan(self.currentState, strategy='bfs', multi_goal=True)

            nextAction = self.getNextJointAction()
            self.executeAction(nextAction, multi_goal=True)
                    # self.agents[int(closest_agent.name)].occupied = True
                    # self.currentState.helping_goals.remove(goal)
        for agent in available_agents:
            agent.goal = None
            agent.status = None
            agent.occupied = False
            agent.current_plan = []
            self.currentState.helping_goals = None

    def getHelpingGoals(self, agents):
        goals = []
        for agent in agents:
            position = self.currentState.find_agent(agent.name)
            goals.append(Atom("Free", position))
            neighbourhood = self.currentState.find_neighbours(position)
            for neighbour in neighbourhood:
                blocking_atom = self.currentState.find_object_at_position(neighbour)
                if blocking_atom is False:
                    goals.append(Atom("Free", neighbour))
                elif blocking_atom.name == "BoxAt":
                    box_color = self.currentState.find_box_color(blocking_atom.variables[0])
                    if box_color == agent.color:
                        goals.append(Atom("Free", neighbour))
        return goals
