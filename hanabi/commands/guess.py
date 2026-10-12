from hanabi import parsing
from hanabi.commands.base import Command, CommandResult

from hanabi.game_objects.exceptions import (
    HanabiException, HanabiIndexException, HanabiInputException,
)


GUESS_TEXT = (
    'The "guess" command, short form "g".  Used to '
    'guess the number or color or a card.\n'
    'Usage:\n'
    'guess <player> <position> <guess>\n'
    'This causes the card at <position> in the hand of <player> to be '
    'updated according to <guess>.\n'
    'Note that this does not advance play; it is just '
    'a way to keep track of thoughts.\n'
    '---> <player> can be a number indicating turn order or a\n'
    '     string which unambiguously identifies the player by name.\n'
    '---> <position> is a number indicating the position\n'
    '     at which to apply <guess>.\n'
    '---> <guess> is a number or a string (not both) '
    'representing the color or number being indicated.\n'
    'Examples:\n'
    'guess 1 4 g (player 1 guesses a green card is at position 4)\n'
    'guess jim 2 5 (the player whose name starts "jim" guesses a 5 is at position 2)\n'
    'guess janos 3 red (player janos guesses a red card is at position 3)\n'
    'guess 0 1 2 (player 0 guesses a 2 is at position 1)'
)

#The logic for the "guess" command
def guess_text(choice, game, verbose=False):
    match choice:
        case [player, position, guess]:
            pass #do nothing, the case statement extracts the values for us
        case [player, position, guess, *args]:
            return game, f'Unrecognized arguments: {", ".join(args)}; try "help guess"'
        case [*args]:
            return game, 'This command requires additional input; try "help guess"'
    try: player = parsing.resolve_player(player, game)
    except HanabiInputException as e: return game, e.args[0]
    try: guess = parsing.read_color_or_number(guess)
    except HanabiInputException as e: return game, e.args[0]
    try: position = int(position)
    except ValueError: return game, f'Invalid position; expected number 1 to 5; yours: {position}'
    #apply the guess
    try: new_state = player.perform_guess(position - 1, guess, game, verbose=verbose)
    except HanabiIndexException as e: return game, f'Card {e.index + 1}: {e.args[0]}'
    except HanabiException as e: return game, e.args[0]
    return new_state, 'Success'


class GuessCommand(Command):

    name = 'guess'
    aliases = ('g',)
    help = {(): GUESS_TEXT}

    def handle(self, options, game, verbose=False):
        new_game, text = guess_text(options, game, verbose=verbose)
        return CommandResult(new_game, text)
