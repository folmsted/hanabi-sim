from hanabi.commands.base import Command, CommandResult
from hanabi.commands.about import AboutCommand
from hanabi.commands.help import HelpCommand
from hanabi.commands.show import ShowCommand
from hanabi.commands._legacy import (
    handle_play, handle_wild_play, handle_hint,
    handle_discard, handle_guess, handle_swap,
)


ABOUT = AboutCommand()
HELP = HelpCommand()
SHOW = ShowCommand()

COMMANDS = (ABOUT, HELP, SHOW)


def find(token):
    """Return the command naming the given token, or None if there is none."""
    for command in COMMANDS:
        if command.matches(token): return command
    return None
