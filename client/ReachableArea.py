from agent import Agent
from atom import Atom
from state import State

class ReachableArea():
    def __init__(self, object_):
        if isinstance(object_, Agent):
            self.agent = object_


    def estimate(self, state: 'State'):
        agt_at = state.find_agent(self.agent.name)


    def union(self) -> 'bool':
        pass



