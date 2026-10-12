from hanabi import parsing
from hanabi.commands.base import Command, CommandResult

from hanabi.game_objects.exceptions import (
    HanabiException, HanabiIndexException, HanabiInputException,
)


HINT_TEXT = (
    'The "hint" command, short form "h".  Used to indicate\n'
    'that the turn player should give a hint to another player.\n'
    'Usage:\n'
    'hint <player> <positions> <hint>\n'
    'This causes the hand of <player> to be updated '
    'according to the <hint> for <positions>.\n'
    '---> <player> can be a number indicating turn order or a\n'
    '     string which unambiguously identifies the player by name.\n'
    '---> <positions> is a space-separated list of numbers\n'
    '     indicating the positions at which to apply the <hint>.\n'
    '---> <hint> is a number or a string (not both) representing\n'
    '     the color or number being indicated.\n'
    'Examples:\n'
    'hint 1 1 3 4 r (player 1 has red cards at positions 1, 3, 4)\n'
    'hint fra 2 5 (the player whose name starts "fra" has a 5 at position 2)\n'
    'hint janos 1 2 3 red (player janos has red cards at positions 1, 2, 3)\n'
    'hint 2 4 5 2 (player 2 has a two card at positions 4, 5)'
)

#The logic for the "hint" command
def hint_text(choice, game, verbose=False):
    match choice:
        case [target_player, *positions, hint]:
            pass #do nothing, the case statement extracts the values for us
        case [*args]:
            return game, 'This command requires additional input; try "help hint"'
    player = game.get_player(game.player_up) #the player whose turn it is
    #resolve target player
    try:
        #player given by turn order
        target_player = int(choice[0]) #the player receiving the hint
        if target_player < 1 or target_player > game.num_players:
            return game, (
                f'Could not find a player {target_player}; '
                f'total players: {game.num_players}'
            )
        target_player = target_player - 1
    except ValueError:
        #player given by name
        target_player = choice[0]
    try: target_player = game.get_player(target_player)
    except HanabiInputException as e: return game, e.args[0]
    #resolve hint
    try: hint = parsing.read_color_or_number(hint)
    except HanabiInputException as e: return game, e.args[0]
    #resolve positions
    if (not positions): return game, 'You must specify positions to hint to.'
    try:
        #correction for convention of 1-indexed cards
        positions = [int(p) - 1 for p in positions]
    except ValueError:
        return game, f'Your indicated positions {", ".join(positions)} were not all integers.'
    #do the hint
    try: new_state = player.perform_hint(target_player, positions, hint, game, verbose=verbose)
    except HanabiIndexException as e: return game, f'Position {e.index + 1}: {e.args[0]}'
    except HanabiException as e: return game, e.args[0]
    return new_state, 'Success; advancing turn'


class HintCommand(Command):

    name = 'hint'
    aliases = ('h',)
    help = {(): HINT_TEXT}

    def handle(self, options, game, verbose=False):
        new_game, text = hint_text(options, game, verbose=verbose)
        return CommandResult(new_game, text)
