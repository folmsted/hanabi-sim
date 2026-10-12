from hanabi import help_text
from hanabi.commands.base import Command, CommandResult


GENERAL_TEXT = \
    'Possible commands (full|shortcut):\nabout|a, help|?, show|s, '\
    'play|p, hint|h, discard|d, guess|g, undo|u, swap, quit|q\n'\
    'Call hint with these arguments for more information on format.'

HELP_TEXT = \
    'The "help" command, short form "?".  You can call help with'\
    ' a command after to get extra information.\n'\
    'Examples:\n'\
    'help s (for help on the "show" command)\n'\
    'help hint (for help on the "hint" command)'

#Help text for commands which are not yet command objects; consulted until
#those commands are converted in a later commit.
_PENDING_HELP = {
    'undo': help_text.help_undo,
    'u': help_text.help_undo,
    'quit': help_text.help_quit,
    'q': help_text.help_quit,
}


class HelpCommand(Command):

    name = 'help'
    aliases = ('?',)
    help = {(): HELP_TEXT}

    def handle(self, options, game):
        return CommandResult(game, self.resolve(options))

    def resolve(self, path):
        """
        Return the help text for the given path of command names, or an
        informative error when the path names no known command or option.
        """
        if not path:
            return GENERAL_TEXT
        from hanabi import commands
        command = commands.find(path[0])
        rest = path[1:]
        if command is not None:
            if command.accepts_subhelp:
                text = command.help_for(rest)
                if text is not None: return text
                return f'Unrecognized arguments {" ".join(rest)}'
            if not rest:
                return command.help_for(())
        elif not rest and path[0] in _PENDING_HELP:
            return _PENDING_HELP[path[0]]
        return f'Did not recognize options {" ".join(path)}'
