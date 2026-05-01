from game_objects import *
import util

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
               case ['graph'] | ['g']:
                   text = util.help_show_graph
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
        case ['graph', *args] | ['g', *args]:
            match args:
                #TODO handle options or resolve not to use options
                case ['play', *options]    | ['p', *options] | \
                     ['discard', *options] | ['d', *options] | \
                     ['misfire', *options] | ['m', *options] | \
                     ['hint', *options] | ['h', *options] if not options:
                    st, tp = ('Play', PlayAction) if args[0] in {'play', 'p'} else          \
                             ('Discard', DiscardAction) if args[0] in {'discard', 'd'} else \
                             ('Misfire', MisfireAction) if args[0] in {'misfire', 'm'} else \
                             ('Hint', HintAction) if args[0] in {'hint', 'h'} else '?????'
                     
                    actions = game.get_actions_of_type(tp)
                    action_takers = [game.players[action[1]].name for action in actions]
                    #Generate map from names to times taking PlayAction
                    data = {
                        name : len([*filter(lambda x: x == name, action_takers)])
                        for name in [p.name for p in game.players]
                    }
                    title = f'{st} Actions by Player'
                    text = util.generate_pie_chart(title, data, util.DEFAULT_CHART_HEIGHT, True)
                case ['hint', 'to',   player] | ['h', 'to',   player] | \
                     ['hint', '>',    player] | ['h', '>',    player] | \
                     ['hint', 'from', player] | ['h', 'from', player] | \
                     ['hint', '<',    player] | ['h', '<',    player] :
                     
                    actions = game.get_actions_of_type(HintAction)
                    try: player_idx = game.players.index(game.get_player(player))
                    except (IndexError, KeyError) as e: return  e.args[0]
                    #filter out hints not from (to) the requested player
                    actions = \
                        filter(lambda x: x[1]==player_idx, actions) if args[1] in {'from', '<'} \
                        else filter(lambda x: x[2].targetplayer_index == player_idx, actions)
                    #TODO add options to make charts of other facts than just hint giver/receiver
                    #get just the name of the hint giver (receiver)
                    actions = \
                        [game.get_player(t[1]).name for t in actions] if args[1] in {'to', '>'} \
                        else [game.get_player(t[2].targetplayer_index).name for t in actions]
                    #don't put the target player in the chart; he can't hint himself
                    #but do put other players in even if they haven't hinted the target
                    #(or been hinted by the target)
                    eligible_players = {p.name for p in game.players} - \
                                       {game.get_player(player_idx).name}
                    data = {p : 0 for p in eligible_players} | util.unique_counts(actions)
                    st = 'to' if args[1] in {'to', '>'} else 'from'
                    title = f'Hints {st} {game.get_player(player_idx).name}'
                    text = util.generate_pie_chart(title, data, util.DEFAULT_CHART_HEIGHT, True)
                case [*args]:
                    text = f'Unrecognized arguments {"".join(args)}; try "help show graph"'
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


