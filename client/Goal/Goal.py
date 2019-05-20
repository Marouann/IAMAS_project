import sys
from state import State
from Tracker import Tracker
from atom import *
from utils import *
from Heuristics.heuristics import *


class Goals:
    @staticmethod
    def prioritize(state: 'State', goals):
        WEIGHT_NEIGHBOURS = 10  # weights for priority
        WEIGHT_DISTANCE = 10  # weight for goal to a box distance
        sorted_goals = list()

        priority = 0

        for name, letter, pos in Goals.prioritize_by_neigbours(state, goals):
            # current_priority = priority +

            sorted_goals.append((name, letter, pos, priority))

            priority += WEIGHT_NEIGHBOURS

        return sorted_goals

    @staticmethod
    def prioritize_by_neigbours(state: 'State', goals):
        # Sort goals 1st by number of free neighbour fields, then by number of neighbour goals)
        sorted_by_neighbour = sorted(goals,
                                     key=lambda x: (state.getNeithbourFieldsWithoutGoals(x[2]).__len__(),
                                                    state.getNeithbourGoals(x[2]).__len__()))
        return sorted_by_neighbour

    @staticmethod
    def prioritize_by_disctance(state: 'State', goals):
        pass

    @staticmethod
    def assign(state: 'State', free_agents, goalsInAction):
        print("Assigning goals", file=sys.stderr)
        (unmet, met) = state.progression()
        if free_agents != []:
            print('\nFree agents : ' + str([agent.name for agent in free_agents]), file=sys.stderr, flush=True)
            print('Goals unmet : ' + str(unmet), file=sys.stderr, flush=True)
            print('Goals already met : ' + str(met), file=sys.stderr, flush=True)
        else:
            # We return to not waste time
            return False

        remaining_agents_to_replan = list(free_agents)

        boxesHandled = []
        # Boxes already placed on the goal
        for name, letter, pos in met:
            boxOnGoal = state.find_box(pos)
            boxesHandled.append(boxOnGoal.variables[0])

        # Boxes that are currently handled by agents
        for agent in state.return_agents():
            if agent.goal is not None:
                boxesHandled.append(agent.goal.variables[0])

        for agent in remaining_agents_to_replan:
            # We update the tracker of the remaining agent.
            agent.update_tracker(state)

            # Each agent that is passed to assignGoals either finished doing its job, or it's his 1st one
            # Hence we if self.goalsInAction contains agent.goal this job has been finished so we need to remove it
            if agent.goal_details in goalsInAction:
                goalsInAction.remove(agent.goal_details)

        for goal in goalsInAction:
            if goal in unmet:
                unmet.remove(goal)

        # We'll store the box tracker to not compute them too many times
        box_tracker_dict = {}
        print("-------------", file=sys.stderr)
        print(unmet, file=sys.stderr)
        prioritizedGoals = Goals.prioritize(state, unmet)

        for priority_goal in prioritizedGoals:

            if remaining_agents_to_replan == []:
                break
            elif priority_goal in goalsInAction:
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
                    if box['letter'] == priority_goal[1] and box['name'] not in boxesHandled:
                        # If it's ok, we can check if the goal and the box are connected
                        box_position = state.find_box_position(box['name'])
                        if state.check_if_connected(priority_goal[2], box_position):
                            boxes_able_to_fill_goal.append((box, box_position))

                # If no boxes can fill the goal right now we skip this goal
                if boxes_able_to_fill_goal == []:
                    continue

                boxes_able_to_fill_goal = sorted(boxes_able_to_fill_goal,
                                                 key=lambda x: state.find_box_goal_distance(x[0]["name"],
                                                                                            priority_goal))

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
                    agent_position = state.find_agent(agent.name)
                    '''
                        We check if the agent and the goal are connected, if not we search for another agent
                        Right now we know:
                            - which box can fill the goal
                            - the agent can move thoses boxes

                        As we already have checked if the boxes_able_to_fill_goal are connected to the goal,
                        we will not need to check if agent and box are connected
                    '''
                    if not state.check_if_connected(agent_position, priority_goal[2]):
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
                        for goalmet in met:
                            boxPlaced = state.find_box(goalmet[2])
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
                                    box_tracker.estimate(state)

                                # Then we see if the goal is reachable from the box or if the goal is reachable from agent
                                # If yes --> we can assign a goal
                                box_can_reach_goal = priority_goal[2] in box_tracker.reachable
                                agent_can_reach_goal = priority_goal[2] in agent.tracker.reachable

                                if self.isSAlvl or box_can_reach_goal or agent_can_reach_goal or agent.ghostmode:
                                    agent.occupied = True
                                    agent.assignGoal(Atom("BoxAt", box['name'], priority_goal[2]), priority_goal)
                                    goalsInAction.append(priority_goal)
                                    boxesHandled.append(box['name'])
                                    # The goal will be assigned to agent, we can update the two following variables
                                    prioritized_goal_is_assigned = True
                                    remaining_agents_to_replan.remove(agent)

                                    agent.plan(state)
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
