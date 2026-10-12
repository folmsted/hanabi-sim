from hanabi.commands.base import Command, CommandResult


UNDO_TEXT = \
    'The "undo" command, short form "u".  Used to revert to the previous game state.\n'\
    'Usage:\n'\
    'undo'

#The logic for the "undo" command
def undo_text(options, game):
    if options: return game, f'Unrecognized options: {", ".join(options)}'
    if game.previous_state:
        text = (
            f'Reverting to prior state; round: {game.previous_state.round}, '
            f'player up: {game.previous_state.players[game.previous_state.player_up].name}'
        )
        game = game.previous_state
    else: text = 'Cannot revert; no previous state to revert to'
    return game, text


class UndoCommand(Command):

    name = 'undo'
    aliases = ('u',)
    help = {(): UNDO_TEXT}

    def handle(self, options, game):
        new_game, text = undo_text(options, game)
        return CommandResult(new_game, text)
