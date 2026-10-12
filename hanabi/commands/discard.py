from hanabi import parsing
from hanabi.commands.base import Command, CommandResult

from hanabi.game_objects.exceptions import (
    HanabiException, HanabiIndexException, HanabiInputException,
)


DISCARD_TEXT = \
    'The "discard" command, short form "d".  Used to '\
    'indicate that turn player should discard a card.\n'\
    'Usage:\n'\
    'discard <position> <card>\n'\
    'This causes the turn player to discard his card '\
    'in position <position> of his hand.\n'\
    '---> <card> is a value which indicates what value the card had on being revealed.\n'\
    '---> <card> is formatted as <color><number> or '\
    '<number><color>; abbreviations allowed.\n'\
    'Examples:\n'\
    'discard 1 1y (player discards card in position 1, which was a yellow 1)\n'\
    'discard 5 3green (player discards card in position 3, which was a green 3)\n'\
    'discard 2 r1 (player discards card in position 2, which was a red 1)'

#The logic for the "discard" command
def discard_text(choice, game, verbose=False):
    match choice:
        case [position, card]:
            pass #do nothing, the case statement extracts the values for us
        case [position, card, *args]:
            return game, f'Unrecognized arguments: {", ".join(args)}; try "help discard"'
        case [*args]:
            return game, 'This command requires additional input; try "help discard"'
    try: card = parsing.read_card(card)
    except HanabiInputException as e: return game, e.args[0]
    try: position = int(position)
    except ValueError as e: return game, f'The specified position ({position}) is not an integer.'
    player = game.get_player(game.player_up)
    try: new_state = player.perform_discard(position - 1, card, game, verbose=verbose)
    except HanabiIndexException as e: return game, f'Card {e.index + 1}: {e.args[0]}'
    except HanabiException as e: return game, e.args[0]
    return new_state, 'Success; advancing turn'


class DiscardCommand(Command):

    name = 'discard'
    aliases = ('d',)
    help = {(): DISCARD_TEXT}

    def handle(self, options, game, verbose=False):
        new_game, text = discard_text(options, game, verbose=verbose)
        return CommandResult(new_game, text)
