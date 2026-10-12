class HanabiRulesException(Exception):
    """
    Used when an action would break a rule of Hanabi.
    Example: hinting oneself.
    """
    def __init__(self, *args):
        super().__init__(*args)

    def __str__(self):
        return f'{self.message}'

class HanabiSimException(Exception):
    """
    Used when an action doesn't make sense in the context of
    the current simulation.
    Example: Discarding the red 5 when it is already played
    """
    def __init__(self, *args):
        super().__init__(*args)

    def __str__(self):
        return f'{self.message}'

#Useful when a problem occurs 
class HanabiIndexException(Exception):
    """
    Used when an action doesn't make sense, and the action takes
    place at a particular index in a hand which it is useful to
    propagate upwards to functions which can print errors based on it.
    Because indexing is different in the objects (0-based) and the
    user interface (1-based), game objects should just raise these errors
    with the index they understand and let the higher functions decide
    how to handle them (usually by adding 1).
    """
    def __init__(self, index, *args):
        super().__init__(*args)
        self.index = index

class HanabiUserInputRequiredException(Exception):
    """
    Used when additional input is required from the user to complete a
    command.  For example, when rainbow cards are set to wild play mode
    and the choice of which firework to apply a rainbow card to must
    be resolved.
    """

    def __init__(self, *args):
        super().__init__(*args)
        
