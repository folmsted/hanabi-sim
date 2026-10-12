from hanabi.commands.base import Command, CommandResult
from hanabi.commands.about import AboutCommand
from hanabi.commands.help import HelpCommand
from hanabi.commands.show import ShowCommand
from hanabi.commands.play import PlayCommand, WildPlayCommand
from hanabi.commands.hint import HintCommand
from hanabi.commands.discard import DiscardCommand
from hanabi.commands.guess import GuessCommand
from hanabi.commands.swap import SwapCommand


ABOUT = AboutCommand()
HELP = HelpCommand()
SHOW = ShowCommand()
PLAY = PlayCommand()
HINT = HintCommand()
DISCARD = DiscardCommand()
GUESS = GuessCommand()
SWAP = SwapCommand()

#The internal follow-up to a "play" that needs a color chosen; not in COMMANDS.
WILD_PLAY = WildPlayCommand()

COMMANDS = (ABOUT, HELP, SHOW, PLAY, HINT, DISCARD, GUESS, SWAP)


def find(token):
    """Return the command naming the given token, or None if there is none."""
    for command in COMMANDS:
        if command.matches(token): return command
    return None
