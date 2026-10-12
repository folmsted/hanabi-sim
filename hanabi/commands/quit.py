from hanabi.commands.base import Command, CommandResult


QUIT_TEXT = (
    'The "quit" command, short form "q".  Used to quit the simulation.\n'
    'Usage:\n'
    'quit'
)


class QuitCommand(Command):

    name = 'quit'
    aliases = ('q',)
    help = {(): QUIT_TEXT}

    def handle(self, options, game):
        if options:
            return CommandResult(game, f'Unrecognized options: {", ".join(options)}')
        game.over = True
        return CommandResult(game, 'Quitting game', stop=True)
