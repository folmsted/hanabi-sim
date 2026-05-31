import readline
import argparse
import input_handling as ih

import util
from game_objects import *

 
if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='hanabi_sim',
                                     description='A tracker for public information in hanabi',
    )
    parser.add_argument('-i', '--infile')
    parser.add_argument('-o', '--outfile')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    outfile_name, outfile = (args.outfile, None) if args.outfile else (None, None)
    infile_name,  infile  = (args.infile,  None) if args.infile  else (None, None)
    verbose = args.verbose
    setup_choices = []
    if infile_name:
        try:
            infile = open(infile_name, 'r')
            setup_choices = infile.readlines()
            infile.close()
        except:
            if infile: del infile
            print(f'Error reading infile; {infile_name}; infile use aborted.')
    if outfile_name:
        outfile = open(outfile_name, 'w')

    color_picker = util.generate_color()
    try: rules = util.get_rules(setup_choices, outfile, color_picker)
    except (KeyboardInterrupt, EOFError):
        print('\nProgram terminated by user.')
        exit(0)
    try: players, protocols = util.get_players(setup_choices, outfile, color_picker)
    except (KeyboardInterrupt, EOFError):
        print('\nProgram terminated by user.')
        exit(0)
    game = GameState(players, protocols, ruleset=rules)

    while (True):
        prompt = f'Ask for information with "?" or make a play '\
                 f'(player up: {game.get_player(game.player_up).name}):'
        if game.over:
            prompt = 'The last play would have caused the end of the game; undo (N/y)?'
        try:
            choice = setup_choices.pop(0).strip() if setup_choices else \
                     input(style_text(next(color_picker), prompt))
        except (KeyboardInterrupt, EOFError):
            print('\nProgram terminated by user.')
            exit(0)
        if outfile:
            outfile.write(choice + '\n')
        choice = util.trim_comment(choice, util.COMMENT_START).split()
        match choice:
            #if the game was ended by the last turn taken, give a chance to back out
            case ['y'] | ['Y'] if game.over:
                text = f'Reverting to prior state; round: {game.previous_state.round}, '\
                f'player up: {game.previous_state.players[game.previous_state.player_up].name}'\
                if game.previous_state else 'Cannot revert; no previous state to revert to'
                game = game.previous_state if game.previous_state else game
                print(text)
            case _ if game.over:
                break
            #otherwise, proceed with the next round
            case []:
                continue
            case ['help', *options] | ['?', *options]:
                print(ih.handle_help(options))
            case ['about', *options] | ['a', *options]:
                print(ih.handle_about(options))
            case ['show', *options] | ['s', *options]:
                print(ih.handle_show(options, game))
            case ['play', *options] | ['p', *options]:
                try: game, text = ih.handle_play(options, game, verbose=verbose)
                except HanabiUserInputRequiredException as e:
                    colors, card, position, table = e.args
                    print(table)
                    #TODO make input gathering a function
                    prompt = 'Select from the table above which color '\
                             'firework to apply this card to:'
                    try: choice = setup_choices.pop(0).strip() if setup_choices else \
                                  input(style_text(next(color_picker), prompt))
                    except (KeyboardInterrupt, EOFError):
                        print('\nProgram terminated by user.')
                        exit(0)
                    if outfile: outfile.write(choice + '\n')
                    game, text = ih.handle_wild_play(
                        colors, choice, card, position, game, verbose=verbose
                    )
                print(text)
            case ['hint', *options] | ['h', *options]:
                game, text = ih.handle_hint(options, game, verbose=verbose)
                print(text)
            case ['discard', *options] | ['d', *options]:
                game, text = ih.handle_discard(options, game, verbose=verbose)
                print(text)
            case ['guess', *options] | ['g', *options]:
                game, text = ih.handle_guess(options, game, verbose=verbose)
                print(text)
            case ['undo', *options] | ['u', *options]:
                if options:
                    text = f'Unrecognized options: {", ".join(options)}'
                else:
                    text = f'Reverting to prior state; round: {game.previous_state.round}, '\
                    f'player up: {game.previous_state.players[game.previous_state.player_up].name}'\
                    if game.previous_state else 'Cannot revert; no previous state to revert to'
                    game = game.previous_state if game.previous_state else game
                print(text)
            case ['swap', *options]:
                game, text = ih.handle_swap(options, game, verbose=verbose)
                print(text)
            case ['quit', *options] | ['q', *options]:
                if options:
                    text = f'Unrecognized options: {", ".join(options)}'
                else:
                    text = 'Quitting game'
                    game.over = True
                    break
                print(text)

    if outfile:
        outfile.close()
    print('Game is over')
    choice = ''
    while (True):
        try:
            choice = input(style_text(next(color_picker),\
                       'You may inquire about the game, but not make plays,'\
                       ' discards, or hints (\'q\' exits):'))
        except (KeyboardInterrupt, EOFError):
            print('\nProgram terminated by user.')
            exit(0)

        choice = choice.split()
        if (not choice):
            continue
        if (choice[0] == 'help' or choice[0] == '?'):
            print(ih.handle_help(choice[1:]))
        if (choice[0] == 'show' or choice[0] == 's'):
            print(ih.handle_show(choice[1:], game))
        if (choice[0] == 'quit' or choice[0] == 'q'):
            break

