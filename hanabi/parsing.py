from hanabi.game_objects.color import Color
from hanabi.game_objects.card import Card
from hanabi.game_objects.exceptions import HanabiInputException


COMMENT_START = '//'


def get_color_from_str(s):
    match s:
        case s if 'blue'      .startswith(s.lower()): return Color.BLUE
        case s if 'green'     .startswith(s.lower()): return Color.GREEN
        case s if 'red'       .startswith(s.lower()): return Color.RED
        case s if 'white'     .startswith(s.lower()): return Color.WHITE
        case s if 'yellow'    .startswith(s.lower()): return Color.YELLOW
        case s if 'multicolor'.startswith(s.lower()): return Color.MULTICOLOR
        #'r' maps to red not rainbow
        case s if 'rainbow'   .startswith(s.lower()): return Color.MULTICOLOR
        case _ : raise HanabiInputException(f'Input {s} does not correspond to any color.')

def trim_comment(string, comment_delimiter=COMMENT_START):
    """
    Search for any part of a string which comes after the given comment_delimiter
    Return a string which omits this portion.
    """
    x = string.find(comment_delimiter)
    return string if x == -1 else string[:x]

def read_card(s):
    """
    Given a user-input string representing a card, (specifying number and color),
    return a Card object with the specified values or error correctly
    """
    n = -1
    c = None
    try:
        n = int(s[0])
        c = get_color_from_str(s[1:])
    except (ValueError, HanabiInputException):
        try:
            n = int(s[-1])
            c = get_color_from_str(s[:-1])
        except (ValueError, HanabiInputException):
            raise HanabiInputException(f'You must specify a number and color; your input: {s}')
    if not (1 <= n <= 5): raise HanabiInputException(f'Illegal number ({n}) given.')
    if not isinstance(c, Color): raise HanabiInputException(f'Illegal color ({c}) given.')
    return Card(c, n)

def read_color_or_number(user_input):
    """
    Given a user-input string, which should specify a single color or number,
    (but not both), return the associated integer value or Color or error correctly.
    """
    try:
        ret = int(user_input)
        if not 1 <= ret <= 5: raise ValueError
    except ValueError:
        try: ret = get_color_from_str(user_input)
        except HanabiInputException:
            raise HanabiInputException(
                f'Invalid value; expected number or color; yours: {user_input}'
            )
    return ret

#Given possibly bad user input, return the corresponding player or error correctly
def resolve_player(choice, game):
    try:
        #See if the input is an integer in closed interval [1, num_players]
        player_request = int(choice) - 1
    except ValueError:
        #Otherwise, assume the value is a player name in the form of a string
        player_request = choice
    if isinstance(player_request, int) and player_request < 0:
        raise HanabiInputException(
            f'Select a player by entering a positive integer; yours: {player_request + 1}'
        )
    return game.get_player(player_request)
