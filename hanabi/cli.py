import readline
import argparse
import random

from hanabi.commands import (
    ABOUT, HELP, SHOW, PLAY, WILD_PLAY, HINT, DISCARD, GUESS, UNDO, SWAP, QUIT,
)
from hanabi.parsing import trim_comment, COMMENT_START
from hanabi.setup import get_rules, get_players
from hanabi.game_objects.game_state import GameState
from hanabi.game_objects.styling import style_text, prompt_colorer

from hanabi.game_objects.exceptions import (
    HanabiRulesException, HanabiSimException, HanabiUserInputRequiredException,
)

DETERMINISTIC_SEED = 0


def main(argv=None):

    parser = argparse.ArgumentParser(
        prog='hanabi_sim',
        description='A tracker for public information in hanabi',
    )
    parser.add_argument('-i', '--infile')
    parser.add_argument('-o', '--outfile')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument(
        '-d', '--deterministic', action='store_true',
        help='seed the RNG so randomized output is reproducible',
    )
    args = parser.parse_args(argv)
    if args.deterministic: random.seed(DETERMINISTIC_SEED)
    outfile_name, outfile = (args.outfile, None) if args.outfile else (None, None)
    infile_name,  infile  = (args.infile,  None) if args.infile  else (None, None)
    verbose = args.verbose
    setup_choices = []
    if infile_name:
        try:
            infile = open(infile_name, 'r')
            setup_choices = infile.readlines()
            infile.close()
        except OSError:
            if infile: del infile
            print(f'Error reading infile; {infile_name}; infile use aborted.')
    if outfile_name: outfile = open(outfile_name, 'w')

    try: rules = get_rules(setup_choices, outfile, prompt_colorer)
    except (KeyboardInterrupt, EOFError):
        print('\nProgram terminated by user.')
        return 0
    try: players, protocols = get_players(setup_choices, outfile, prompt_colorer)
    except (KeyboardInterrupt, EOFError):
        print('\nProgram terminated by user.')
        return 0
    try: game = GameState(players, protocols, ruleset=rules)
    except (HanabiRulesException, HanabiSimException) as e:
        raise RuntimeError(f'Unhandled game initialization error: {e.args[0]}') from e

    while (True):
        prompt = (
            f'Ask for information with "?" or make a play '
            f'(player up: {game.get_player(game.player_up).name}):'
        )
        if game.over: prompt = 'The last play would have caused the end of the game; undo (N/y)?'
        try:
            choice = (
                setup_choices.pop(0).strip() if setup_choices
                else input(style_text(next(prompt_colorer), prompt))
            )
        except (KeyboardInterrupt, EOFError):
            print('\nProgram terminated by user.')
            return 0
        if outfile: outfile.write(choice + '\n')
        choice = trim_comment(choice, COMMENT_START).split()
        match choice:
            #if the game was ended by the last turn taken, give a chance to back out
            case ['y'] | ['Y'] if game.over:
                text = (
                    f'Reverting to prior state; round: {game.previous_state.round}, '
                    f'player up: {game.previous_state.players[game.previous_state.player_up].name}'
                    if game.previous_state else 'Cannot revert; no previous state to revert to'
                )
                game = game.previous_state if game.previous_state else game
                print(text)
            case _ if game.over:
                break
            #otherwise, proceed with the next round
            case []:
                continue
            case [command, *options] if HELP.matches(command):
                print(HELP.handle(options, game).text)
            case [command, *options] if ABOUT.matches(command):
                print(ABOUT.handle(options, game).text)
            case [command, *options] if SHOW.matches(command):
                print(SHOW.handle(options, game).text)
            case [command, *options] if PLAY.matches(command):
                try:
                    result = PLAY.handle(options, game, verbose=verbose)
                except HanabiUserInputRequiredException as e:
                    print(e.args[3])
                    try:
                        choice = (
                            setup_choices.pop(0).strip() if setup_choices
                            else input(style_text(next(prompt_colorer), WILD_PLAY.prompt))
                        )
                    except (KeyboardInterrupt, EOFError):
                        print('Program terminated by user.')
                        exit(0)
                    if outfile: outfile.write(choice + '\n')
                    result = WILD_PLAY.handle(e.args, choice, game, verbose=verbose)
                game, text = result.game, result.text
                print(text)
            case [command, *options] if HINT.matches(command):
                result = HINT.handle(options, game, verbose=verbose)
                game, text = result.game, result.text
                print(text)
            case [command, *options] if DISCARD.matches(command):
                result = DISCARD.handle(options, game, verbose=verbose)
                game, text = result.game, result.text
                print(text)
            case [command, *options] if GUESS.matches(command):
                result = GUESS.handle(options, game, verbose=verbose)
                game, text = result.game, result.text
                print(text)
            case [command, *options] if UNDO.matches(command):
                result = UNDO.handle(options, game)
                game = result.game
                print(result.text)
            case [command, *options] if SWAP.matches(command):
                result = SWAP.handle(options, game, verbose=verbose)
                game, text = result.game, result.text
                print(text)
            case [command, *options] if QUIT.matches(command):
                result = QUIT.handle(options, game)
                game = result.game
                if result.stop: break
                print(result.text)

    if outfile: outfile.close()
    print('Game is over')
    choice = ''
    #allow users to view statistics about the finished game before ending the program
    while (True):
        try:
            choice = input(
                style_text(
                    next(prompt_colorer),
                    'You may inquire about the game, but not make plays,'
                    ' discards, or hints (\'q\' exits):',
                )
            )
        except (KeyboardInterrupt, EOFError):
            print('\nProgram terminated by user.')
            return 0

        choice = choice.split()
        if (not choice): continue
        if (HELP.matches(choice[0])):
            print(HELP.handle(choice[1:], game).text)
        if (SHOW.matches(choice[0])):
            print(SHOW.handle(choice[1:], game).text)
        if (QUIT.matches(choice[0])): break
    return 0

