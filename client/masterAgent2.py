import argparse
import re
import sys
import numpy as np
import random
#from collections import deque

from state import State
from atom import Atom
from agent import *
from action import *
from knowledgeBase import KnowledgeBase
from utils import *
from Tracker import Tracker


class MasterAgent:
    def __init__(self, initial_state: 'State', agents: '[Agent]', boxes: '[dict]'):
        self.currentState = initial_state

        self.agents = []
        self.boxes = boxes  # List of { 'name': Box, 'letter': char, 'color': color }
        self.goalsInAction = []
        self.previous_actions = None
        self.blocked_goals = {}

        for agt in sorted(agents, key=lambda k: k['name']):
            agtAt = initial_state.find_agent(agt['name'])
            agent = Agent(agt['name'], agtAt, None, [Move, Push, Pull, NoOp], agt['color'])
            self.agents.append(agent)

        self.isSAlvl = 1 == len(self.agents)

    def prioritizeGoals(self, goals):
        # Sort goals 1st by number of free neighbour fields, then by number of neighbour goals)
        sortedGoals = sorted(goals,
                                key=lambda x: (self.currentState.getNeithbourFieldsWithoutGoals(x["position"]).__len__(),
                                self.currentState.getNeithbourGoals(x["position"]).__len__()))

        return sortedGoals

    def assignGoals(self, agentsToReplan):
        print("Assigning goals", file=sys.stderr)
        (goalsToAssign, goalsMet) = self.currentState.get_unmet_goals()
        if agentsToReplan != []:
            print('\nFree agents : ' + str([agent.name for agent in agentsToReplan]), file=sys.stderr, flush=True)
            print('Goals unmet : ' + str(goalsToAssign), file=sys.stderr, flush=True)
            print('Goals already met : ' + str(goalsMet), file=sys.stderr, flush=True)
        else:
            # We return to not waste time
            return

        remaining_agents_to_replan = list(agentsToReplan)

        boxesHandled = []
        # Boxes already placed on the goal
        for goal in goalsMet:
            boxOnGoal = self.currentState.find_box(goal['position'])
            boxesHandled.append(boxOnGoal.variables[0])

        # Boxes that are currently handled by agents
        for agent in self.agents:
            if agent.goal is not None:
                boxesHandled.append(agent.goal.variables[0])

        for agent in remaining_agents_to_replan:
            # We update the tracker of the remaining agent.
            agent.update_tracker(self.currentState)

            # Each agent that is passed to assignGoals either finished doing its job, or it's his 1st one
            # Hence we if self.goalsInAction contains agent.goal this job has been finished so we need to remove it
            if agent.goal_details in self.goalsInAction:
                self.goalsInAction.remove(agent.goal_details)

        for goal in self.goalsInAction:
            if goal in goalsToAssign:
                goalsToAssign.remove(goal)

        # We'll store the box tracker to not compute them too many times
        box_tracker_dict = {}
        print("-------------", file=sys.stderr)
        print(goalsToAssign, file=sys.stderr)
        prioritizedGoals = self.prioritizeGoals(goalsToAssign)
        for prioritized_goal in prioritizedGoals:

            if remaining_agents_to_replan == []:
                break
            elif prioritized_goal in self.goalsInAction:
                # print('Goal has already been assigned : ' + str(goal), file=sys.stderr, flush=True)
                continue
            else:
                prioritized_goal_is_assigned = False
                agents_connected = []

                '''
                    We filter the box to retains the one that can fill the goal and that are not already handled
                    We do it once for all agents.
                '''
                boxes_able_to_fill_goal = []
                for box in self.boxes:
                    # First we check if the letter is ok and if the box is not already handled (we already have the info)
                    if box['letter'] == prioritized_goal['letter'] and box['name'] not in boxesHandled:
                        # If it's ok, we can check if the goal and the box are connected
                        box_position = self.currentState.find_box_position(box['name'])
                        if self.currentState.check_if_connected(prioritized_goal['position'], box_position):
                            boxes_able_to_fill_goal.append((box, box_position))

                # If no boxes can fill the goal right now we skip this goal
                if boxes_able_to_fill_goal == []:
                    continue

                boxes_able_to_fill_goal = sorted(boxes_able_to_fill_goal,
                                            key=lambda x: self.currentState.find_box_goal_distance(x[0]["name"], prioritized_goal))

                for agent in remaining_agents_to_replan:
                    # If the goal is alreay assigned, we stop searching an agent that can achieve it

                    if prioritized_goal_is_assigned:
                        break
                    # If agent is occupied or if he has already a goal
                    # or if its color is not the same than the boxes we skip it
                    if agent.occupied != False or \
                        agent.goal is not None or \
                        agent.color != boxes_able_to_fill_goal[0][0]['color']:
                        # print('Agent already has a goal, continue: ' + str(goal), file=sys.stderr, flush=True)
                        continue

                    # Here we know that agent is not occupied and it has no goal.
                    if agent.current_plan != []:
                        print(agent.name, agent.current_plan[0], file=sys.stderr, flush=True)
                    else:
                        print('Agent', agent.name, 'has no plan!', file=sys.stderr, flush=True)

                    # We get the position of the agent
                    agent_position = self.currentState.find_agent(agent.name)
                    '''
                        We check if the agent and the goal are connected, if not we search for another agent
                        Right now we know:
                            - which box can fill the goal
                            - the agent can move thoses boxes

                        As we already have checked if the boxes_able_to_fill_goal are connected to the goal,
                        we will not need to check if agent and box are connected
                    '''
                    if not self.currentState.check_if_connected(agent_position, prioritized_goal['position']):
                        # print('Goal:', goal['position'],'is not connected with the agent', 'agent', agent_position, file=sys.stderr, flush=True)
                        continue

                    ''' We can add store the information that agent can achieve this goal'''
                    agents_connected.append((agent, agent_position))

                    ''' For the box that can fill the goal, we'll try to assign a goal to the agent '''
                    prioritizedBoxes = list(boxes_able_to_fill_goal)
                    while prioritizedBoxes != [] and not prioritized_goal_is_assigned:
                        (box, box_pos) = prioritizedBoxes.pop(0)

                        # We avoid assigning a box that is already placed on a goal.
                        boxAlreadyPlaced = False
                        for goalmet in goalsMet:
                            boxPlaced = self.currentState.find_box(goalmet['position'])
                            if boxPlaced.variables[0] == box['name']:
                                boxAlreadyPlaced = True

                        if not boxAlreadyPlaced:
                            if box_pos in agent.tracker.boundary or agent.ghostmode:
                                box_tracker = None
                                # We initiate a tracker at the box position
                                if str(box_pos) in box_tracker_dict:
                                    box_tracker = box_tracker_dict[str(box_pos)]
                                else:
                                    box_tracker = Tracker(box_pos)
                                    box_tracker_dict[str(box_pos)] = box_tracker
                                    box_tracker.estimate(self.currentState)

                                # Then we see if the goal is reachable from the box or if the goal is reachable from agent
                                # If yes --> we can assign a goal
                                box_can_reach_goal = prioritized_goal['position'] in box_tracker.reachable
                                agent_can_reach_goal = prioritized_goal['position'] in agent.tracker.reachable

                                if  box_can_reach_goal or agent_can_reach_goal or agent.ghostmode:
                                    agent.occupied = True
                                    agent.assignGoal(Atom("BoxAt", box['name'], prioritized_goal['position']), prioritized_goal)
                                    self.goalsInAction.append(prioritized_goal)
                                    boxesHandled.append(box['name'])
                                    # The goal will be assigned to agent, we can update the two following variables
                                    prioritized_goal_is_assigned = True
                                    remaining_agents_to_replan.remove(agent)


                                    agent.plan(self.currentState, strategy="astar")
                                    if agent.current_plan == []:
                                        agent.status = STATUS_REPLAN_NO_PLAN_FOUND
                                else:
                                    print('The box and the agent can not reach the goal', file=sys.stderr)
                                    agent.ghostmode = True

                            else:
                                print('Box placed in: ', box_pos, 'is not reachable', file=sys.stderr)
                                agent.ghostmode = True

                if not prioritized_goal_is_assigned:
                    print('Goal not assigned yet', file=sys.stderr)

                print(prioritized_goal_is_assigned, file=sys.stderr)


        for agent in agentsToReplan:
            print('agent: ' + str(agent.name) + ', has goal: ' + str(agent.goal), file=sys.stderr, flush=True)

    def solveLevel(self):
        # We need to check the goal.

        self.assignGoals(self.agents)

        # Store previous and current joint actions
        self.previous_actions = [ [] for _ in self.agents]
        for agt_index in range(len(self.agents)):
            action = {'action': NoOp, 'params': [str(agt_index), self.currentState.find_agent(str(agt_index))],
                                    'message':'NoOp',
                                    'priority':4}

            '''
            We want to keep the last to actions for conflict management, previous_action needs to be initialized with length 2
            '''
            self.previous_actions[agt_index].append(action)    # [ pop(0) <-[Previous joint action], [Current joint action] <- append(jointaction)]
            self.previous_actions[agt_index].append(action)

        # counter in while
        nb_iter = 0

        # remember if last action has been successful because during conflict solving action are performed successfuly
        # even if the conflict is not totally solved
        old_valids = [False,False, False]
        old_nb_free_agents = 0
        nb_free_agents = 0
        # stop util reached goal
        while self.currentState.get_unmet_goals()[0] != []:
            # print(self.currentState.get_unmet_goals()[0], file=sys.stderr)
            nb_iter += 1

            # First we loop over agent to free them if their goal are met
            free_agents = [agent for agent in self.agents if agent.occupied == False]

            '''
            Only re-assign goal if some agents have finished their task in the previous
            iteration. That prevents to go through all goals when no potential agent
            can pick a goal. Particularly helpful for levels that have many goals.
            '''

            old_nb_free_agents = nb_free_agents
            nb_free_agents = len(free_agents)
            print(nb_free_agents, file=sys.stderr)
            print(old_nb_free_agents, file=sys.stderr)
            if nb_free_agents != old_nb_free_agents or nb_iter % 20 == 0 :
                self.assignGoals(free_agents)

            # Gets the first actions from each agent (joint action on first row)
            actions_to_execute = self.getNextJointAction()


            # Keep the response from the server ([true, false, ...])

            old_valids.pop(0)
            valid = self.executeAction(actions_to_execute)
            old_valids.append(isAllExecuted(valid))

            # 'agents_with_conflit': List of agents which cannot execute their actions (e.g [agt0, agt1, agt6])
            agents_with_conflit = [i for i in range(len(valid)) if valid[i]=='false']

            # If 'agents_with_conflit' not empty then solve conflict
            if agents_with_conflit != []:
                self.solveConflict(agents_with_conflit)
                # self.solveConflict(agents_with_conflit,actions_to_execute, previous_action)

            for agent in self.agents:
                print('Agents', agent.name, file=sys.stderr)
                print('Status', agent.status, file=sys.stderr)
                print('occupied', agent.occupied, file=sys.stderr)
                print(agent.goal, file=sys.stderr)
                print(agent.goal_details, file=sys.stderr)
                print('plan length', len(agent.current_plan), file=sys.stderr)

            print(old_valids, file=sys.stderr)
            if False not in old_valids:
                self.replanAgentWithStatus(STATUS_REPLAN_AFTER_CONFLICT)

            # Replan for agents that have goals but no plan
            self.replanAgentWithStatus(STATUS_WAIT_REPLAN)

            if nb_iter % 5 == 0:
                self.replanAgentWithStatus(STATUS_REPLAN_NO_PLAN_FOUND)
                for agent in self.agents:
                    if agent.current_plan == [] and agent.goal not in self.currentState.atoms and agent.status == None:
                        agent.status = STATUS_REPLAN_GHOST
                    if agent.status == STATUS_NOT_REPLAN:
                        agent.status = None
                        agent.occupied = False

                self.replanAgentWithStatus(STATUS_REPLAN_GHOST)

            #
            # if nb_iter > 15:
            #     break




    def replanAgentWithStatus(self, status:'int'):
        for agent in self.agents:
            if agent.status == status and agent.goal is not None:
                print('Replanning with status', agent.status, file=sys.stderr)

                if status == STATUS_REPLAN_GHOST:
                    agent.ghostmode = True
                else:
                    agent.ghostmode = False
                isGoalReachable = True
                if agent.ghostmode == False:
                    agent.update_tracker(self.currentState)
                    boxPos = self.currentState.find_box_position(agent.goal.variables[0])
                    isGoalReachable = boxPos in agent.tracker.reachable and agent.goal.variables[1] in agent.tracker.reachable
                if isGoalReachable:
                    agent.plan(self.currentState)
                    if agent.current_plan != []:
                        agent.status = None
                        agent.occupied = True
                else:
                    '''
                    if an agent cannot be replan without ghost mode, it will try to replan
                    at next iteration with ghost mode.
                    '''
                    print("agent is not replan", agent.name, file=sys.stderr)
                    print(self.currentState.find_agent(agent.name), file=sys.stderr)
                    agent.status = STATUS_REPLAN_GHOST


            elif agent.status == status and agent.goal is None:
                # agent without goals are freed.
                agent.occupied = False
                agent.status = None



    def getNextJointAction(self):
        # initialize joint_action with 'NoOp' of length number of agents ['NoOp', 'NoOp', 'NoOp', ...]
        joint_action = []
        for agent in self.agents:
            # If there are still actions in current plan pop the first action and
            if agent.current_plan != [] :
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
        print('**********************', file=sys.stderr)
        for i, action in enumerate(jointAction):
            if action['message'] != 'NoOp':
                self.previous_actions[i].append(action)
                self.previous_actions[i].pop(0)

        for agent_action in jointAction:
            actions_string += agent_action['message']
            actions_string += ';'

        actions_string = actions_string[:-1]  # remove last ';' from the string


        print('Action set to server:', actions_string, file=sys.stderr, flush=True)  # print out


        # retrieve answer from server and separate answer for specific action
        # [:-1] is only to remove the '\n' at the end of response
        print(actions_string, flush=True)  # send to server
        server_answer = sys.stdin.readline()[:-1].split(";")

        print('Server response : ' + str(server_answer), file=sys.stderr, flush=True)
        print('**********************', file=sys.stderr)
        for agent in self.agents:
            print(agent.name, self.currentState.find_agent(agent.name), file=sys.stderr)
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

    def solveConflict(self, agents_with_conflict):
        print('Conflict found', file=sys.stderr)
        remaining_agents_with_conflict = list(agents_with_conflict)
        # First we check if now the action is applicable:
        # Conflict type 1.
        '''
        Conflict type 1: at execution the agent was not able to perform its action
        but as other agents move, it now can execute it.

        Solution: stop other agents and make the agent with a conflict execute its
        last executed action.
        '''
        for i in agents_with_conflict:
            action = self.previous_actions[i][1]
            if action['action'].checkPreconditions(self.currentState, action['params']):
                # if the action is applicable, we apply it while stopping the others agents.
                jointAction = [{'action': NoOp, 'params': [str(agt_index), self.currentState.find_agent(str(agt_index))],
                                    'message':'NoOp',
                                    'priority':4} for agt_index in range(len(self.agents))]
                jointAction[i] = action
                remaining_agents_with_conflict.remove(i)
                print("Executing action to solve type 1 conflict", file=sys.stderr)
                self.executeAction(jointAction)


        '''
         If the agent can not apply its action there is two caseS possible:
         - The agent is conflicting alone, he wants to go on an occupied cell.
            But the "blocker" can continue its way without conflicting
               => We can make the agent wait or ask for help if the blocker does not plan to move.
         - Two agents are trying to go on the same way
               => We need to prioritize someone.

         First we need to know what is blocking
         To do so, we need to check the unmet preconditions of agent that are conflicting.

         A dict will be created, where each conflicting agent A has it entry:
         The values in here are a list of dict containing informations about agents conflicting with A.

         Example:

         {0: [{'agent': 1, 'status': 'moving', 'success': True, 'unmet_precond': <atom.Atom object at 0x7fcc7c1c8ac8>, 'priority': 1}]}
        '''


        who_is_conflicting_with = {}
        key_to_remove = []
        for current_agent_index in remaining_agents_with_conflict:
            who_is_conflicting_with[current_agent_index] = []

            action = self.previous_actions[current_agent_index][1]
            print(action, file=sys.stderr)
            preconds = action['action'].preconditions(*action['params'])
            unmet_preconds = []
            for atom in preconds:
                if atom not in self.currentState.atoms and atom not in self.currentState.rigid_atoms:
                    unmet_preconds.append(atom)


            # Now we want to know which agent has unmet this precondition
            for other_agent in [agt for agt in self.agents if int(agt.name) != current_agent_index]:
                other_agent_index = int(other_agent.name)
                # We check if the other_agent was able to performs its action
                print("remaining:", remaining_agents_with_conflict, file=sys.stderr)
                if other_agent_index in remaining_agents_with_conflict:
                    '''
                    Conflict type 3:
                    More than one agent did not perform their last actions
                    --> We need to look at actions executed one step before to find the origin of the conflict, i.e in previous_action
                    '''
                    print('More than one conflicting agent', file=sys.stderr)

                    other_agent_is_the_problem = False
                    unmet_precond_due_to_other_agent = None
                    last_action = None

                    '''
                    Finding what action among the last 2 actions of the other agent has unmet the precond
                    '''
                    for t in [1, 0]:
                        other_action = self.previous_actions[other_agent_index][t]
                        print("Other agent action", other_action, file=sys.stderr)
                        neg_effects = other_action['action'].negative_effects(*other_action['params'])

                        for atom in unmet_preconds:
                            if atom in neg_effects and not other_agent_is_the_problem:
                                other_agent_is_the_problem = True
                                unmet_precond_due_to_other_agent = atom
                                last_action = other_action

                    # if the other agent has unmet the precondition it is added to the dict who_is_conflicting_with
                    if other_agent_is_the_problem:
                        who_is_conflicting_with[current_agent_index].append({
                            'agent': other_agent_index,
                            'status': 'blocked', # blacked ?
                            'success': False,
                            'unmet_precond': unmet_precond_due_to_other_agent,
                            'priority': len(self.agents[current_agent_index].current_plan)
                        })
                        unmet_preconds.remove(unmet_precond_due_to_other_agent)


                else:
                    '''
                    Conflict type 2:
                    The agent is alone in the conflict: other agents were able to execute their action
                    But we still to detect which agent has unmet the predcondition even if succeed
                    to do its action.
                    '''


                    other_agent_is_the_problem = False
                    unmet_precond_due_to_other_agent = None
                    last_action = None

                    '''
                    Finding what action among the last 2 actions of the other agent has unmet
                    the precond.
                    '''

                    for t in [1, 0]:
                        other_action = self.previous_actions[other_agent_index][t]
                        neg_effects = other_action['action'].negative_effects(*other_action['params'])
                        for atom in unmet_preconds:

                            if atom in neg_effects and not other_agent_is_the_problem:
                                other_agent_is_the_problem = True
                                unmet_precond_due_to_other_agent = atom
                                last_action = other_action

                    # If the agent is the problem, we have to store that it in conflicting with current_agent_index
                    if other_agent_is_the_problem:

                        who_is_conflicting_with[current_agent_index].append({
                            'agent': other_agent_index,
                            'status': 'moving',
                            'success': True,
                            'unmet_precond': unmet_precond_due_to_other_agent,
                            'priority': len(self.agents[current_agent_index].current_plan)
                        })
                        unmet_preconds.remove(unmet_precond_due_to_other_agent)

            if unmet_preconds != []:
                '''
                If there are still some unmet preconditions, it means that agent is in ghostmode
                and tries to move into a box.

                In that case:
                    --> first we try to replan without ghostmode
                    --> if the goal or the box is not reachable have to solve the conflict.
                '''
                print('Unmet precond:', unmet_preconds[0], file=sys.stderr)
                box = self.currentState.find_box(unmet_preconds[0].variables[0])
                if box is not False:
                    print('Ghostmode agent run into a box!', file=sys.stderr)
                    agent = self.agents[current_agent_index]

                    #the agent problem is taken into account we don't want it in the rest of conflict solving
                    key_to_remove.append(int(agent.name))
                    agent.ghostmode = False
                    keep_plan = agent.current_plan.copy()
                    agent.current_plan = []

                    #update tracker of the agent so he has the current state
                    agent.update_tracker(self.currentState)

                    print('Agent:', agent.name, file=sys.stderr)
                    print(agent.goal.variables[1], file=sys.stderr)
                    print("Boundary", agent.tracker.boundary, file=sys.stderr)
                    goalBoxPosition = self.currentState.find_box_position(agent.goal.variables[0])
                    box_tracker = Tracker(goalBoxPosition)
                    box_tracker.estimate(self.currentState)
                    if agent.goal.name == 'BoxAt' and goalBoxPosition in agent.tracker.boundary \
                        and (agent.goal.variables[1] in box_tracker.boundary or agent.goal.variables[1] in box_tracker.reachable) :
                        agent.plan(self.currentState)
                        print("here", file=sys.stderr)
                    if agent.current_plan == []:
                        #first put last action in plan cause it has not been executed
                        agent.current_plan = keep_plan
                        agent.current_plan.insert(0, action)
                        self.solveGhostBoxConflict(agent, box)


        print("who is conflicting", who_is_conflicting_with, file=sys.stderr)



        for key, value in who_is_conflicting_with.items():
            if value == [] and key not in key_to_remove:

                key_to_remove.append(key)
                agent_to_replan = self.agents[key]
                agent_to_replan.current_plan = []
                # agent_to_replan.goal = None
                agent_to_replan.ghostmode = False
                agent_to_replan.status = STATUS_WAIT_REPLAN
                # agent_to_replan.occupied = False

        print('key to remove', key_to_remove, file=sys.stderr)
        '''
        Now that we have found the agents that are in the conflict, we need to find
        solution to it.

        First we divide conflicts into clusters of conflicts: their may be 2 different
        conflicts happening at the same moment.
        Then we solved then separately.

        '''


        conflict_clusters = get_cluster_conflict(who_is_conflicting_with, key_to_remove)
        print('conflict clusters', conflict_clusters, file=sys.stderr)
        for cluster in conflict_clusters:
            prioritization_needed = False
            for current_agent_index  in cluster:

                conflicting_agents = who_is_conflicting_with[current_agent_index]
                # First, if there is only one agent that is conflicting:

                print("Conclicting agents", conflicting_agents, file=sys.stderr)

                if len(conflicting_agents) == 1:
                    conflicting_agent = conflicting_agents[0]

                    # Conflict TYPE 2
                    if conflicting_agent['success']:
                        # for agent in self.agents:
                        #     self.agents[agent].current_plan.insert(0, {'action': NoOp,
                        #                                 'params': [agent.name, self.currentState.find_agent(agent.name)],
                        #                                 'message':'NoOp',
                        #                                 'priority':4})
                        self.agents[current_agent_index].current_plan.insert(0, self.previous_actions[current_agent_index][1])
                        self.executeConflictSolution(self.agents[conflicting_agent['agent']],
                                                    conflicting_agent['unmet_precond'],
                                                    cluster)
                    # Conflict TYPE 3
                    else:
                        '''
                        In that case, no solution can be found easily, agents are in deadlock.
                        We need to prioritize them and choose a conflict solver.
                        '''
                        prioritization_needed = True

            if prioritization_needed:
                print("Prioritization needed", cluster,  file=sys.stderr)

                # agent that has the longest plan is freed first from the conflict
                priority_agent = max(cluster, key=lambda key: who_is_conflicting_with[key][0]['priority'])
                conflict_solver = who_is_conflicting_with[priority_agent][0]['agent']
                conflict_solution = who_is_conflicting_with[priority_agent][0]['unmet_precond']
                print("Conflict solution:", conflict_solution, file=sys.stderr)
                for agent in self.agents:
                    self.agents[int(agent.name)].current_plan.insert(0, {'action': NoOp,
                                                'params': [agent.name, self.currentState.find_agent(agent.name)],
                                                'message':'NoOp',
                                                'priority':4})
                for agent in cluster:
                    self.agents[agent].current_plan.insert(0, self.previous_actions[agent][1])
                self.executeConflictSolution(self.agents[conflict_solver],
                                            conflict_solution,
                                            cluster)


    '''
    This function store the goal of an agent while he executes the solution of a conflict.
    Takes the conflict solver, the solution of the conflict (i.e. the atom that needs to be met)
    and the set of agents that are in the same conflict.
    '''
    def executeConflictSolution(self, agent:'Agent', solution:'Atom', conflicting_with = None):
        # first keep agent goal information
        goal_keep = agent.goal
        goal_details_keep = agent.goal_details
        agent.current_plan = []
        agent.occupied = True
        agent.goal = solution
        agent.goal_details = None
        agent.status = STATUS_SOLVING_CONFLICT

        # plan for the solution and set other agents in conflict's actions to NoOp
        agent.ghostmode = False
        object_in_conflict = self.currentState.find_object_at_position(solution.variables[0])
        if object_in_conflict is not False:
            if object_in_conflict.name == "BoxAt" and agent.color == self.currentState.find_box_color(object_in_conflict.variables[0]):
                agent.plan(self.currentState, strategy="bfs")
                for other_agent in conflicting_with:
                    if other_agent != int(agent.name):
                        self.agents[other_agent].current_plan.insert(0,{
                            'action': NoOp,
                            'params': [other_agent, self.currentState.find_agent(other_agent)],
                            'message':'NoOp',
                            'priority':4,
                        })
            elif object_in_conflict.name == "AgentAt" and object_in_conflict.variables[0] == agent.name:
                agent.plan(self.currentState, strategy="bfs")
                for other_agent in conflicting_with:
                    if other_agent != int(agent.name):
                        self.agents[other_agent].current_plan.insert(0,{
                            'action': NoOp,
                            'params': [other_agent, self.currentState.find_agent(other_agent)],
                            'message':'NoOp',
                            'priority':4,
                        })

        if len(agent.current_plan) == 0:
            '''
             Conflict TYPE 4: conflict solver is blocked need to reverse priority.
             This is a complete deadlock.
             In that case, we drop goals of agents in conflict and plan for a more
             complex solution where all agents in conflict are participating.

            '''
            print("Conflict solver is blocked, need help", file=sys.stderr)
            print(conflicting_with, file=sys.stderr)
            agent.occupied = False
            agent.status = STATUS_DEADLOCK
            agent.ghostmode = False

            # at this point we stop keeping in memory information of the previous goal
            # we will need to fully replan after the conflict is solved.
            # self.goalsInAction.remove(goal_details_keep)
            self.goalsInAction = []
            for agent_index in conflicting_with:
                self.agents[agent_index].occupied = False
                self.agents[agent_index].status = STATUS_DEADLOCK

            available_agents = [agent for agent in self.agents if agent.status == STATUS_DEADLOCK]
            available_agents = available_agents + self.find_neighbours_agents(available_agents)
            print('Available agents are', available_agents, file=sys.stderr)
            self.unlock_deadlock(available_agents, agent, goal_keep)
        else:
            '''
            If conflict solution has been found, agent retrieve its goal and wait for a replanning
            '''

            agent.goal = goal_keep
            agent.goal_details = goal_details_keep
            agent.ghostmode = False
            agent.status = STATUS_REPLAN_AFTER_CONFLICT


    def find_neighbours_agents(self, agents):
        old_length = -1
        while len(agents) != old_length:
            old_length = len(agents)
            for agent in agents:
                agentPos = self.currentState.find_agent(agent.name)
                neighbourhood = self.currentState.find_neighbours(agentPos)
                for cell in neighbourhood:
                    atom = self.currentState.find_object_at_position(cell)
                    if atom is not False and atom.name == "AgentAt" and self.agents[int(atom.variables[0])] not in agents:
                        agents.append(self.agents[int(atom.variables[0])])
        return agents

    '''
    This function finds a solution to deadlock between a group of agents.
    '''
    def unlock_deadlock(self, available_agents, priority_agent, goal):

        '''
        First we compute goals to be achieved: we want to free all cells around each agent.
        But only cell that the given agent can interact with.

        Example: 0 and A are blue while B is red.
        +++++
        +0A +
        +B+++
        +++++

        Then we want to free (1,1) and (2,1) but not (1,2).
        '''

        self.currentState.helping_goals = self.getHelpingGoals(available_agents)

        print("Agents available here", file=sys.stderr)
        for agent in available_agents:
            print(agent.name, file=sys.stderr)
            print(self.currentState.find_agent(agent.name), file=sys.stderr)


        '''
        Now we want to find a solution for this.
        The idea here is to plan for a multi goal with bfs. (Add depth limit to stop?)
        '''
        iter = 0
        while not areGoalsMet(self.currentState, self.currentState.helping_goals):
            iter += 1
            print("\n\n\n\n\n\n", iter, file=sys.stderr)
            print("Helping goal:", file=sys.stderr)

            for goal in self.currentState.helping_goals:
                print(goal, file=sys.stderr)

            '''
            First we divide goals between agents: for that we look at what is on the cell
            we want to free.
             - if it's an agent, the agent on that cell is responsible for that.
             - if it's box, the agent is responsible only if it's the same color.
             - if it's already free, all agent are responsible for that.
            '''
            responsible = {} # dict used to divide goals between different agents
            for agent in available_agents:
                agentPos = self.currentState.find_agent(agent.name)
                freeAgentAt = Atom("Free", agentPos)
                if freeAgentAt not in self.currentState.helping_goals:
                    self.currentState.helping_goals.append(freeAgentAt)
                responsible[agent.name] = set()

            for goal in self.currentState.helping_goals:
                obstructed_by = self.currentState.find_object_at_position(goal.variables[0])

                if obstructed_by is not False and obstructed_by.name == 'AgentAt':
                    responsible[obstructed_by.variables[0]].add(goal)

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
                        responsible[closest_agent.name].add(goal)
                else:
                    for agent in available_agents:
                        responsible[agent.name].add(goal)


            '''
            All agents now plan for their own goals.
            '''
            for name, goals in responsible.items():
                self.agents[int(name)].goal = list(goals)
                self.agents[int(name)].ghostmode = False
                self.agents[int(name)].current_plan = []
                self.agents[int(name)].plan(self.currentState, strategy='astar', multi_goal=True, max_depth=20)
                # self.agents[int(name)].plan(self.currentState, strategy='astar', multi_goal=True, max_depth=10)
                self.executeActionOnlyForAgents([self.agents[int(name)]], multi_goal=True)

            nextAction = []

            # self.executeActionOnlyForAgents([self.agents[int(key)] for key in responsible.keys()], multi_goal=True)


            print("Goal achievable", self.currentState.isGoalAchievable(priority_agent, goal), file=sys.stderr)
            if self.currentState.isGoalAchievable(priority_agent, goal) or iter > 15:
                break
            print("goal division:", responsible, file=sys.stderr)

        '''
        Conflict solution has been found, now agents are freed and can be assign to new
        or past goals.
        '''

        for agent in self.agents:
            agent.goal = None
            agent.status = None
            agent.occupied = False
            agent.current_plan = []
            self.currentState.helping_goals = None

        # replan_agent = self.agents[3]
        # replan_agent.status = None
        # replan_agent.occupied = True


    def getHelpingGoals(self, agents):
        goals = []
        for agent in agents:
            position = self.currentState.find_agent(agent.name)
            goals.append(Atom("Free", position))
            neighbourhood = self.currentState.find_neighbours(position)
            for neighbour in neighbourhood:
                blocking_atom = self.currentState.find_object_at_position(neighbour)
                if blocking_atom is False:
                    pass
                    # goals.append(Atom("Free", neighbour))
                elif blocking_atom.name == "BoxAt":
                    box_color = self.currentState.find_box_color(blocking_atom.variables[0])
                    if box_color == agent.color:
                        goals.append(Atom("Free", neighbour))
        return goals


    '''
    Solving issue when agents run into boxes when being in ghostmode.

    Two cases:
    - the box is of the same color: plan for free the cell of the box and agent at the same place
        (might be improved by using safe spaces, careful that safe spaces are actually reachables)
      then continue plan.
    - the box is of another color: need help.
       --> find an helping agent and make it plan for Free the cell (might be improved by using safe spaces as well)
       --> then the helper agent may not be able to reach the problematic box. In that case, the other agent also plan
            to free its own cell as he is probably blocking the helper.

            Example: ++++++++  where 1 and B are blue and A and 0 red.
                      10 BAA+
                     ++++++++
            More examples can be found in level BoxBlocking_v2.lvl
    '''
    def solveGhostBoxConflict(self, agent, box):
        print(box, file=sys.stderr)
        boxColor = self.currentState.find_box_color(box.variables[0])
        agentsOfSameColor = [agent for agent in self.agents if agent.color == boxColor]
        if agent in agentsOfSameColor: ## Could be useful for SA levels
            if len(agentsOfSameColor) == 1:
                agentPos = self.currentState.find_agent(agent.name)
                print("Box is the same color as the agent", file=sys.stderr)


                #actual_safe_cells = list(map(lambda cell: (self.currentState.find_distance(cell, agentPos), cell),
                 #                           self.currentState.safe_cells))

                #sorted_actual_safe_cells = sorted([cell for cell in actual_safe_cells if cell[0]>0], key=lambda cell: cell[0])


                cell_found = False
                #while not cell_found and sorted_actual_safe_cells != []:
                 #   cell = sorted_actual_safe_cells.pop()

                if self.currentState.return_safe(agent.name):
                    freeGoal = [Atom('BoxAt', box.variables[0], self.currentState.return_safe(agent.name))]
                    cell_found = True
                else:
                    freeGoal = [Atom('Free', box.variables[1])]
                # freeGoal = [Atom('Free', box.variables[1])]

                keep_goal = agent.goal
                keep_plan = agent.current_plan.copy()
                agent.ghostmode = False
                agent.current_plan = []

                agent.goal = freeGoal
                # print(agent.goal[0], agent.goal[1], file=sys.stderr)
                agent.plan(self.currentState, strategy='astar', multi_goal=True)
                print(agent.current_plan, file=sys.stderr)

                self.executeActionOnlyForAgents([agent])

                agent.goal = keep_goal
                agent.ghostmode = True
                agent.plan(self.currentState)
            else:
                agent.goal = None
                agent.status = None
                agent.occupied = False
                agent.current_plan = []

        else:
            print("Box is not of the same other color as the agent, need help", file=sys.stderr)
            helper, boxReachable = self.findHelpingAgent(agent, box)
            if helper is not None:
                helper.current_plan = []
                if boxReachable:
                    print("Helper is agent", helper.name, file=sys.stderr)
                    print("He can reach the box! ", file=sys.stderr)
                    helper.goal = Atom('Free', self.currentState.find_box_position(box.variables[0]))
                    helper.ghostmode = False
                    helper.plan(self.currentState, strategy='astar')
                    self.executeActionOnlyForAgents([helper])
                elif boxReachable is not None:
                    print("Helper is agent", helper.name, file=sys.stderr)
                    print("He can not reach the box! ", file=sys.stderr)
                    agent.current_plan = []

                    agent.goal = [Atom('Free', self.currentState.find_agent(agent.name))]
                    helper.goal = [Atom('Free', self.currentState.find_agent(agent.name)),
                                   Atom('Free', self.currentState.find_box_position(box.variables[0]))]

                    agent.ghostmode = False
                    agent.plan(self.currentState, strategy='bfs', multi_goal=True, max_depth=1)
                    print("Agent plan", agent.current_plan, file=sys.stderr)
                    self.executeActionOnlyForAgents([agent], multi_goal=True)


                    helper.ghostmode = False
                    helper.plan(self.currentState, strategy='astar', multi_goal=True)
                    self.executeActionOnlyForAgents([helper], multi_goal=True)
                    print("Agent plan", agent.current_plan, file=sys.stderr)
                    print("Helper plan", helper.current_plan, file=sys.stderr)


                helper.goal = None
                agent.goal =None
                helper.occupied = False
                agent.ghostmode = False
                helper.ghostmode = False
                agent.occupied =False

    def findHelpingAgent(self, agentToHelp: 'Agent', boxBlocking: 'Atom') -> 'Agent':
        '''
        check if box is same color and reachable by an agent
         --> yes he is helper
         --> no, check if box is same color and both agent can reach each other
            --> yes select this agent
        '''
        boxColor = self.currentState.find_box_color(boxBlocking.variables[0])
        boxPos = boxBlocking.variables[1]
        possibleHelpingAgents = [agent for agent in self.agents if agent.color == boxColor]


        for agent in possibleHelpingAgents:
            agent.update_tracker(self.currentState)
            if boxPos in agent.tracker.boundary:
                return  (agent, True)

        # if box is not reachable for any agents find agent that can reach the agent that needs help

        for agent in possibleHelpingAgents:
            agentToHelpPos = self.currentState.find_agent(agentToHelp.name)
            if agentToHelpPos in agent.tracker.boundary:
                return  (agent, False)

        print("Helping agent not found", file=sys.stderr)
        return (None, None)

    def executeActionOnlyForAgents(self, agentList, multi_goal=False):
        loop_on = True
        while True in [agent.current_plan != [] for agent in agentList]:
            nextAction = [{'action': NoOp,
                                        'params': [agent.name, self.currentState.find_agent(agent.name)],
                                        'message':'NoOp',
                                        'priority':4} for agent in self.agents]
            for agent in agentList:
                if agent.current_plan != []:
                    action = agent.current_plan.pop(0)
                    if action['action'].checkPreconditions(self.currentState, action['params']):
                        nextAction[int(agent.name)] = action
                    else:
                        loop_on = False
                        print("Action not executed", file=sys.stderr)
                        agent.current_plan = []
                        # agent.current_plan.insert(0, action)

            valid = self.executeAction(nextAction, multi_goal=True)
            # agents_with_conflict = [i for i in range(len(valid)) if valid[i]=='false']
            # if agents_with_conflict != []:
            #     self.solveConflict(agents_with_conflict)
