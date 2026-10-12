from hanabi import parsing
from hanabi.commands.base import Command, CommandResult

from hanabi.game_objects.exceptions import (
    HanabiException, HanabiIndexException, HanabiInputException,
)


SWAP_TEXT = \
    'The "swap" command (no short form).  Used to '\
    'swap the positions of two cards in a player\'s hand.\n'\
    'Usage:\n'\
    'swap <player> <position1> <position2>\n'\
    'This causes the card at position <position1> to be placed into <position2>.\n'\
    ' and the card in <position2> to be placed in <position1>\n'\
    'Note that this does not advance play; it just '\
    'changes the order of cards in the hand.\n'\
    '---> <player> can be a number indicating turn order or a\n'\
    '     string which unambiguously identifies the player by name.\n'\
    '---> <position1> and <position2> are integers indicating\n'\
    '     the positions of the cards to swap.\n'\
    'Examples:\n'\
    'swap 1 4 5 (player 1 swaps the cards at positions 4 and 5)\n'\
    'swap sigismund 2 5 (the player whose name starts "sigismund" '\
    'swaps the cards at positions 2 and 5)'

#The logic for the "swap" command
def swap_text(choice, game, verbose=False):
    match choice:
        case [player, index1, index2]:
            pass #do nothing; the case statement extracts the values for us
        case [player, index1, index2, *args]:
            #too many options
            return game, f'Unrecognized arguments: {", ".join(args)}; try "help swap"'
        case [*args]:
            #too few options
            return game, 'This command requires additional input; try "help swap"'
    try: player = parsing.resolve_player(player, game)
    except HanabiInputException as e: return game, e.args[0]
    try: index1, index2 = int(index1), int(index2)
    except ValueError: return game, f'Integers expected as indices; yours: {index1, index2}'
    try: new_state = player.perform_swap(index1 - 1, index2 - 1, game, verbose=verbose)
    except HanabiIndexException as e: return game, f'Card {e.index + 1}: {e.args[0]}'
    except HanabiException as e: return game, e.args[0]
    return new_state, 'Success'


class SwapCommand(Command):

    name = 'swap'
    help = {(): SWAP_TEXT}

    def handle(self, options, game, verbose=False):
        new_game, text = swap_text(options, game, verbose=verbose)
        return CommandResult(new_game, text)
