from hanabi.commands.base import Command, CommandResult


ABOUT_TEXT = (
    'This is hanabi-sim, a simulator for the public information '
    'available in a game of Hanabi.\n'
    'This tool tracks all the information which would be available '
    'to a person with the following properties:\n'
    '1) He hears all hints given, and knows the givers and recipients\n'
    '2) He knows the identities of all cards discarded and played, '
    'and the composition of the Hanabi deck\n'
    '3) He does NOT see the cards of any player; what he knows about '
    'hands is purely by hint information\n'
    '4) He has perfect memory of what he has seen and heard\n'
    'By inputting to hanabi-sim the moves in a game of Hanabi, '
    'including the hints, plays, and discards,\n'
    'you should be able to access all information you know about '
    'your own hand, and all the information which\n'
    'your partners know about their hands.  Use the "help" command '
    'for more specific information on usage.'
)


class AboutCommand(Command):
    name = 'about'
    aliases = ('a',)
    help = {(): ABOUT_TEXT}

    def handle(self, options, game):
        if options:
            return CommandResult(game, f'Did not recognize options {" ".join(options)}.')
        return CommandResult(game, ABOUT_TEXT)
