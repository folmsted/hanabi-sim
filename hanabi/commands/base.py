class CommandResult:
    """
    The outcome of running a command: the (possibly unchanged) game, the
    text to display, and whether the command ends the session.
    """

    def __init__(self, game, text, stop=False):
        self.game = game
        self.text = text
        self.stop = stop


class Command:
    """
    A single user command.  Subclasses set the identifying attributes and
    the table of help strings, and implement handle to run the command.
    """

    name = ''
    aliases = ()
    accepts_subhelp = False
    help = {}

    def handle(self, options, game):
        """
        Carry out this command for the given options and game, returning a
        CommandResult.  Subclasses supply the code needed to process the
        command, or to return a result explaining why it cannot proceed.
        """
        raise NotImplementedError

    def matches(self, token):
        """Return whether the given token names this command."""
        return token == self.name or token in self.aliases

    def help_for(self, path):
        """
        Return the help text for the given sub-path beneath this command,
        or None when no such help exists.
        """
        return self.help.get(tuple(path))
