from hanabi.commands.base import Command, CommandResult


HELP_TEXT = (
    'The "help" command, short form "?".  You can call help with'
    ' a command after to get extra information.\n'
    'Examples:\n'
    'help s (for help on the "show" command)\n'
    'help hint (for help on the "hint" command)'
)


def _general_text():
    """
    Build the general help text from the command registry, so the list of
    commands and shortcuts can never drift from the commands themselves.
    """
    from hanabi import commands
    labels = []
    for command in commands.COMMANDS:
        label = command.name if not command.aliases else f'{command.name}|{command.aliases[0]}'
        labels.append(label)
    return (
        'Possible commands (full|shortcut):\n'
        f'{", ".join(labels)}\n'
        'Call help with a command for more information on format.'
    )


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
            return _general_text()
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
        return f'Did not recognize options {" ".join(path)}'
