from agent import Agent
from atom import Atom
from state import State

class ReachableArea():
    def __init__(self, object_):
        if isinstance(object_, Agent):
            self.agent = object_


    def estimate(self, state: 'State'):
        reachable = set()
        frontier = set()


        current_cell = state.find_agent(self.agent.name)
        reachable.add(current_cell)
        frontier = set()
        frontier.add(current_cell)
        possible_directions = []
        while frontier:
            for cell in frontier:
                state.find_neighbour()







    def union(self) -> 'bool':
        pass


    def comp
