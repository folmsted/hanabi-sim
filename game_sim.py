from enum import Enum
import random
import readline
import argparse

import util
from game_objects import *

def handle_help(choice):
    """
    Print the appropriate information according to user input.
    """
    text = ''
    #no options given
    match choice:
        case []:
           text = util.help_general
        case ['about'] | ['a']:
           text = util.help_about
        case ['help'] | ['?']:
           text = util.help_help
        case ['show', *args] | ['s', *args]:
           match args:
               case ['info'] | ['i']:
                   text = util.help_show_info
               case []:
                   text = util.help_show
               case _:
                   text = f'Unrecognized arguments {" ".join(args)}'
        case ['play'] | ['p']:
           text = util.help_play
        case ['hint'] | ['h']:
           text = util.help_hint
        case ['discard'] | ['d']:
           text = util.help_discard
        case ['guess'] | ['g']:
           text = util.help_guess
        case ['undo'] | ['u']:
           text = util.help_undo
        case ['swap']: #TODO 'w' as a short form?
           text = util.help_swap
        case ['quit'] | ['q']:
           text = util.help_quit
        case _:
            text = f'Did not recognize options {" ".join(choice)}'
    return text

def handle_about(options):
    if options: return f'Did not recognize options {" ".join(options)}.'
    return util.help_about

#The logic for the "show" command
def handle_show(choice, game):
    match choice:
        case []:
            text = 'This command requires further arguments; try "help show"'
        case ['outstanding'] | ['o']:
            text = str(game.outstanding_cards) + '\n'
            text += f'Number outstanding (including in hands): {len(game.outstanding_cards)}'
        case ['state'] | ['s']:
            text = game.represent_general()
        case ['play'] | ['p']:
            text = game.represent_play()
        case ['discard'] | ['d']:
            text = game.represent_discard()
        case ['card', player, position] | ['c', player, position]:
            try: player = util.resolve_player(player, game)
            except (ValueError, IndexError, KeyError) as e: return e.args[0]
            try: position = int(position)
            except ValueError: return f'Expected an integer card position; yours: {position}.'
            if not 1 <= position <= len(player.hand):
                return f'Position {position} is out of range'
            text = f'{player.name} card {position}:\n{player.represent_card(position - 1)}'
        case ['card', *args] | ['c', *args]:
            text = 'Additional input required for card histroy; see "help show"'
        case ['hand', *args] | ['h', *args]:
            if len(args) > 1: return f'Unrecognized arguments {", ".join(args)}; try "help show"'
            try: player_request = args[0]
            except: player_request = game.player_up + 1 #default is player up
            try: player = util.resolve_player(player_request, game)
            except (KeyError, IndexError) as e: return e.args[0]
            text = str(player)
        case ['info', *args] | ['i', *args]:
            match args:
                case ['play', *sort] | ['p', *sort]:
                    actions = game.get_actions_of_type(PlayAction)
                    header = ['index', 'round', 'player', 'card']
                    try: action_metadata = util.sort_stats_playdiscardmisfire(actions, sort)
                    except HanabiSimException as e: return e.args[0]
                    rows = [
                        [index + 1,
                         md.rnd + 1,
                         game.players[md.player].name,
                         md.action.card
                        ] for index, md in enumerate(action_metadata)
                    ]
                    text = tabulate(rows, headers=header, tablefmt='pretty')
                case ['discard', *sort] | ['d', *sort]:
                    actions = game.get_actions_of_type(DiscardAction)
                    header = ['index', 'round', 'player', 'card']
                    try: action_metadata = util.sort_stats_playdiscardmisfire(actions, sort)
                    except HanabiSimException as e: return e.args[0]
                    rows = [
                        [index + 1,
                         md.rnd + 1,
                         game.players[md.player].name,
                         md.action.card
                        ] for index, md in enumerate(action_metadata)
                    ]
                    text = tabulate(rows, headers=header, tablefmt='pretty')
                case ['misfire', *sort] | ['m', *sort]:
                    actions = game.get_actions_of_type(MisfireAction)
                    header = ['index', 'round', 'player', 'card']
                    try: action_metadata = util.sort_stats_playdiscardmisfire(actions, sort)
                    except HanabiSimException as e: return e.args[0]
                    rows = [
                        [index + 1,
                         md.rnd + 1,
                         game.players[md.player].name,
                         md.action.card
                        ] for index, md in enumerate(action_metadata)
                    ]
                    text = tabulate(rows, headers=header, tablefmt='pretty')
                case ['hint', *sort] | ['h', *sort]:
                    actions = game.get_actions_of_type(HintAction)
                    header = ['index', 'round', 'giver', 'receiver', 'cards', 'hint']
                    try: action_metadata = util.sort_stats_hints(actions, sort)
                    except HanabiSimException as e: return e.args[0]
                    rows = [
                        [index + 1,
                         md.rnd + 1,
                         game.players[md.player].name,
                         game.players[md.action.targetplayer_index].name,
                         ', '.join([str(p + 1) for p in md.action.positions]),
                         md.action.hint
                        ] for index, md in enumerate(action_metadata)
                    ]
                    text = tabulate(rows, headers=header, tablefmt='pretty')
                case [player_request, *sort] | [player_request, *sort]:
                    try: player = util.resolve_player(player_request, game)
                    except (KeyError, IndexError) as e: return e.args[0]
                    actions = game.get_player_actions(game.players.index(player))
                    #don't care about sorting one player's actions by player, omit it
                    actions = [(rnd, act) for rnd, act in enumerate(actions)]
                    header = ['index', 'round', f'{player.name} action']
                    #TODO make this use metadata and let sorting preserve round data
                    try: actions_metadata = util.sort_stats_players(actions, sort)
                    except Exception as e: raise e #TODO handle error as above
                    rows = [
                        [i + 1,
                        md.rnd + 1,
                        f'Played {md.action.card}'    if isinstance(md.action, PlayAction)    else
                        f'Discarded {md.action.card}' if isinstance(md.action, DiscardAction) else
                        f'Misfired {md.action.card}'  if isinstance(md.action, MisfireAction) else
                        f'Hinted {game.players[md.action.targetplayer_index].name} about '\
                        f'{md.action.hint} at positions ' \
                        f'{", ".join([str(p + 1) for p in md.action.positions])}.'
                        if isinstance(md.action, HintAction)
                        else '?!? Should never happen!'
                        ] for i, md in enumerate(actions_metadata)
                    ]
                    #TODO this sorting option is still garbage.  Make it better somehow
                    text = tabulate(rows, headers=header, tablefmt='pretty')
                case _:
                    text = 'You must specify what information to show; try "help show info".'
        case [*args]:
            text = f'Unrecognized arguments: {", ".join(args)}; try "help show".'
    return text

#The logic for the "play" command
def handle_play(choice, game, verbose=False):
    match choice:
        case [position, card]:
            pass #do nothing, the case statement extracts the values for us
        case [position, card, *args]:
            return game, f'Unrecognized arguments: {", ".join(args)}; try "help play"'
        case [*args]:
            return game, 'This command requires additional input; try "help play"'
    try: card = util.read_card(card)
    except ValueError as e: return game, e.args[0]
    try: position = int(position)
    except ValueError as e: return game, f'The specified position ({position}) is not an integer.'
    player = game.get_player(game.player_up)
    try: new_state = player.perform_play(position - 1, card, game, verbose=verbose)
    except (HanabiSimException, HanabiRulesException) as e: return game, e.args[0]
    except HanabiIndexException as e: return game, f'Card {e.index + 1}: {e.args[0]}'
    #We must kick this one upstairs; we cannot (cleanly) poll the user here
    except HanabiUserInputRequiredException as e: raise e
    return new_state, 'Success; advancing turn'

#The logic for the "play" command after the user plays a rainbow card in wild-play
#mode and has supplied the choice of (valid) color to which the card will apply
def handle_wild_play(colors, choice, card, position, game, verbose=False):
    #valid colors are at least 1 and at most 5, by construction, since there are
    #only ever 5, not 6 suits in wild-play mode because rainbow is not a suit.
    #Therefore we can reuse this function.
    try: choice = util.read_color_or_number(choice)
    except HanabiSimException as e: return game, e.args[0]
    if isinstance(choice, int):
        try: choice = colors[choice - 1]
        except IndexError as e:
            return game, f'Integer must be between 1 and {len(colors)}; yours: {choice}.'
    elif isinstance(choice, Color):
        if choice not in colors:
            return game, f'Your color, {choice}, was not in the table of possible colors.'
    else: return game, f'Unrecognized input {choice}.'

    player = game.get_player(game.player_up)
    try: new_state = player.perform_wild_play(position, card, choice, game, verbose=verbose)
    #TODO check and handle possible exceptions with proper error strings
    except Exception as e: return game, 'NOT IMPLEMENTED'
    return new_state, 'Success; advancing turn'

#The logic for the "hint" command
def handle_hint(choice, game, verbose=False):
    match choice:
        case [target_player, *positions, hint]:
            pass #do nothing, the case statement extracts the values for us
        case [*args]:
            return game, 'This command requires additional input; try "help hint"'
    player = game.get_player(game.player_up) #the player whose turn it is
    #resolve target player
    try:
        #player given by turn order
        target_player = int(choice[0]) #the player receiving the hint
        if target_player < 1 or target_player > game.num_players:
            return game, f'Could not find a player {target_player}; total players: {game.num_players}'
        target_player = target_player - 1
    except:
        #player given by name
        target_player = choice[0]
    try: target_player = game.get_player(target_player)
    except (IndexError, KeyError): return game, e.args[0]
    #resolve hint
    try: hint = util.read_color_or_number(hint)
    except HanabiSimException as e: return game, e.args[0]
    #resolve positions
    if (not positions): return game, 'You must specify positions to hint to.'
    try:
        #correction for convention of 1-indexed cards
        positions = [int(p) - 1 for p in positions]
    except ValueError:
        return game, f'Your indicated positions {", ".join(positions)} were not all integers.'
    #do the hint
    try:
        new_state = player.perform_hint(target_player, positions, hint, game, verbose=verbose)
    except (HanabiRulesException, HanabiSimException) as e:
        return game, e.args[0]
    except HanabiIndexException as e:
        return game, f'Position {e.index + 1}: {e.args[0]}'
    return new_state, 'Success; advancing turn'

#The logic for the "discard" command
def handle_discard(choice, game, verbose=False):
    match choice:
        case [position, card]:
            pass #do nothing, the case statement extracts the values for us
        case [position, card, *args]:
            return game, f'Unrecognized arguments: {", ".join(args)}; try "help discard"'
        case [*args]:
            return game, 'This command requires additional input; try "help discard"'
    try: card = util.read_card(card)
    except ValueError as e: return game, e.args[0]
    try: position = int(position)
    except ValueError as e: return game, f'The specified position ({position}) is not an integer.'
    player = game.get_player(game.player_up)
    try:
        new_state = player.perform_discard(position - 1, card, game, verbose=verbose)
    except HanabiRulesException as e:
        if e.args[0]: return (game, e.args[0])
        return (game, f'Cannot discard position {position}; no such card')
    except HanabiSimException as e:
        return game, e.args[0]
    except HanabiIndexException as e:
        return game, f'Card {e.index + 1}: {e.args[0]}'
    return new_state, 'Success; advancing turn'

#The logic for the "guess" command
def handle_guess(choice, game, verbose=False):
    match choice:
        case [player, position, guess]:
            pass #do nothing, the case statement extracts the values for us
        case [player, position, guess, *args]:
            return game, f'Unrecognized arguments: {", ".join(args)}; try "help guess"'
        case [*args]:
            return game, 'This command requires additional input; try "help guess"'
    try: player = util.resolve_player(player, game)
    except (ValueError, IndexError, KeyError) as e: return game, e.args[0]
    try: guess = util.read_color_or_number(guess)
    except HanabiSimException as e: return game, e.args[0]
    try: position = int(position)
    except ValueError: return game, f'Invalid position; expected number 1 to 5; yours: {position}'
    #apply the guess
    try: new_state = player.perform_guess(position - 1, guess, game, verbose=verbose)
    except HanabiSimException as e: return game, e.args[0]
    except HanabiIndexException as e: return game, f'Card {e.index + 1}: {e.args[0]}'
    return new_state, 'Success' 

#The logic for the "swap" command
def handle_swap(choice, game, verbose=False):
    match choice:
        case [player, index1, index2]:
            pass #do nothing; the case statement extracts the values for us
        case [player, index1, index2, *args]:
            #too many options
            return game, f'Unrecognized arguments: {", ".join(args)}; try "help swap"'
        case [*args]:
            #too few options
            return game, 'This command requires additional input; try "help swap"'
    try: player = util.resolve_player(player, game)
    except (ValueError, IndexError, KeyError) as e: return game, e.args[0]
    try: index1, index2 = int(index1), int(index2)
    except ValueError: return game, f'Integers expected as indices; yours: {index1, index2}'
    try: new_state = player.perform_swap(index1 - 1, index2 - 1, game, verbose=verbose)
    except (ValueError, HanabiSimException) as e:
        return game, e.args[0]
    except HanabiIndexException as e:
        return game, f'Card {e.index + 1}: {e.args[0]}'
    return new_state, 'Success'

 
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

    while (not game.over):
        prompt = f'Ask for information with "?" or make a play '\
                 f'(player up: {game.get_player(game.player_up).name}):' 
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
            case []:
                continue
            case ['help', *options] | ['?', *options]:
                print(handle_help(options))
            case ['about', *options] | ['a', *options]:
                print(handle_about(options))
            case ['show', *options] | ['s', *options]:
                print(handle_show(options, game))
            case ['play', *options] | ['p', *options]:
                try: game, text = handle_play(options, game, verbose=verbose)
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
                    game, text = handle_wild_play(
                        colors, choice, card, position, game, verbose=verbose
                    )
                print(text)
            case ['hint', *options] | ['h', *options]:
                game, text = handle_hint(options, game, verbose=verbose)
                print(text)
            case ['discard', *options] | ['d', *options]:
                game, text = handle_discard(options, game, verbose=verbose)
                print(text)
            case ['guess', *options] | ['g', *options]:
                game, text = handle_guess(options, game, verbose=verbose)
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
                game, text = handle_swap(options, game, verbose=verbose)
                print(text)
            case ['quit', *options] | ['q', *options]:
                if options:
                    text = f'Unrecognized options: {", ".join(options)}'
                else:
                    text = 'Quitting game'
                    game.over = True
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
            print(handle_help(choice[1:]))
        if (choice[0] == 'show' or choice[0] == 's'):
            print(handle_show(choice[1:], game))
        if (choice[0] == 'quit' or choice[0] == 'q'):
            break

