class HanabiException(Exception):
    """
    Base class for unusual conditions the program knows how to resolve.
    Every subclass is expected to be caught somewhere and turned into an
    informative message or a request for further input; a HanabiException
    that reaches the top level indicates a handler is missing.  Genuine
    programmer errors should use built-in exceptions and are allowed to
    crash.  HanabiUserInputRequiredException is deliberately NOT a subclass
    of this, because it is a control-flow signal rather than an error.
    """

class HanabiRulesException(HanabiException):
    """
    Used when an action would break a rule of Hanabi.
    Example: hinting oneself.
    """

class HanabiSimException(HanabiException):
    """
    Used when an action doesn't make sense in the context of
    the current simulation.
    Example: Discarding the red 5 when it is already played
    """

class HanabiInputException(HanabiException):
    """
    Used when the user's input cannot be resolved into a game object or
    argument at all, before any rule or game state is consulted.
    Examples: an unrecognized color word, an integer where a card is
    required, a player name matching nobody, or a player index that does
    not exist.  Input that parses but is disallowed by the rules or
    impossible given the state is a HanabiRules- or HanabiSimException
    instead.
    """

class HanabiIndexException(HanabiException):
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
