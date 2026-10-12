from hanabi import parsing
from hanabi.commands.base import Command, CommandResult
from hanabi.game_objects.color import Color

from hanabi.game_objects.exceptions import (
    HanabiException, HanabiIndexException, HanabiInputException,
    HanabiUserInputRequiredException,
)


PLAY_TEXT = (
    'The "play" command, short form "p".  '
    'Used to indicate that turn player should play a card.\n'
    'Usage:\n'
    'play <position> <card>\n'
    'This causes the turn player to play his card in position <position> of his hand.\n'
    '---> <card> is a value which indicates what value the card had on being revealed.\n'
    '---> <card> is formatted as <color><number> or <number><color>; '
    'one-letter abbreviations allowed.\n'
    'Examples:\n'
    'play 1 1y (player plays card in position 1, which was a yellow 1)\n'
    'play 5 3green (player plays card in position 3, which was a green 3)\n'
    'play 2 r1 (player plays card in position 2, which was a red 1)'
)

WILD_PLAY_PROMPT = 'Select from the above table to which color firework this card applies:'


#The logic for the "play" command
def play_text(choice, game, verbose=False):
    match choice:
        case [position, card]:
            pass #do nothing, the case statement extracts the values for us
        case [position, card, *args]:
            return game, f'Unrecognized arguments: {", ".join(args)}; try "help play"'
        case [*args]:
            return game, 'This command requires additional input; try "help play"'
    try: card = parsing.read_card(card)
    except HanabiInputException as e: return game, e.args[0]
    try: position = int(position)
    except ValueError as e: return game, f'The specified position ({position}) is not an integer.'
    player = game.get_player(game.player_up)
    try: new_state = player.perform_play(position - 1, card, game, verbose=verbose)
    except HanabiIndexException as e: return game, f'Card {e.index + 1}: {e.args[0]}'
    #We must kick this one upstairs; we cannot (cleanly) poll the user here
    except HanabiUserInputRequiredException as e: raise e
    except HanabiException as e: return game, e.args[0]
    return new_state, 'Success; advancing turn'


#The logic for the "play" command once the user has played a rainbow card in
#wild-play mode and supplied the choice of (valid) color to which it applies
def wild_play_text(e_args, choice, game, verbose=False):
    colors, card, position, table = e_args
    #valid colors are at least 1 and at most 5, by construction, since there are
    #only ever 5, not 6 suits in wild-play mode because rainbow is not a suit.
    #Therefore we can reuse this function.
    try: choice = parsing.read_color_or_number(choice)
    except HanabiInputException as e: return game, e.args[0]
    if isinstance(choice, int):
        try: choice = colors[choice - 1]
        except IndexError as e:
            return game, f'Integer must be between 1 and {len(colors)}; yours: {choice}.'
    elif isinstance(choice, Color):
        if choice not in colors:
            return game, f'Your color, {choice}, was not in the table of possible colors.'
    else: return game, f'Unrecognized input {choice}.'

    player = game.get_player(game.player_up)
    try: new_state = player.perform_wild_play(position, card, choice, game, verbose=verbose)
    except HanabiIndexException as e: return game, f'Card {e.index + 1}: {e.args[0]}'
    except HanabiException as e: return game, e.args[0]
    return new_state, 'Success; advancing turn'


class PlayCommand(Command):

    name = 'play'
    aliases = ('p',)
    help = {(): PLAY_TEXT}

    def handle(self, options, game, verbose=False):
        new_game, text = play_text(options, game, verbose=verbose)
        return CommandResult(new_game, text)


class WildPlayCommand(Command):
    """
    The internal follow-up to a "play" whose card requires the user to pick
    a color.  It is never matched by name; cli drives it directly once it has
    read the choice.
    """

    prompt = WILD_PLAY_PROMPT

    def handle(self, e_args, choice, game, verbose=False):
        new_game, text = wild_play_text(e_args, choice, game, verbose=verbose)
        return CommandResult(new_game, text)
