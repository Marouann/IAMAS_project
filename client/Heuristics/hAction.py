from action import Action

class hAction (Action):
    def __init__(self, name, preconditions, positive_effects, negative_effects):
        super().__init__(name=name,
                         preconditions=preconditions,
                         )