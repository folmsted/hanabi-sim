from hanabi.commands.base import Command, CommandResult
from hanabi.commands.about import AboutCommand
from hanabi.commands.help import HelpCommand
from hanabi.commands.show import ShowCommand
from hanabi.commands.play import PlayCommand, WildPlayCommand
from hanabi.commands.hint import HintCommand
from hanabi.commands.discard import DiscardCommand
from hanabi.commands.guess import GuessCommand
from hanabi.commands.swap import SwapCommand
from hanabi.commands.undo import UndoCommand
from hanabi.commands.quit import QuitCommand


ABOUT = AboutCommand()
HELP = HelpCommand()
SHOW = ShowCommand()
PLAY = PlayCommand()
HINT = HintCommand()
DISCARD = DiscardCommand()
GUESS = GuessCommand()
UNDO = UndoCommand()
SWAP = SwapCommand()
QUIT = QuitCommand()

WILD_PLAY = WildPlayCommand()

COMMANDS = (ABOUT, HELP, SHOW, PLAY, HINT, DISCARD, GUESS, UNDO, SWAP, QUIT)


def find(token):
    """Return the command naming the given token, or None if there is none."""
    for command in COMMANDS:
        if command.matches(token): return command
    return None
