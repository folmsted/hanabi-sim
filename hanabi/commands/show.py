from tabulate import tabulate

from hanabi import parsing, reporting, pie_chart
from hanabi.commands.base import Command, CommandResult

from hanabi.game_objects.actions import HintAction, DiscardAction, PlayAction, MisfireAction
from hanabi.game_objects.exceptions import HanabiInputException, HanabiSimException


SHOW_TEXT = \
    'The "show" command, short form "s".  Used to print information.\n'\
    'Usages:\n'\
    'show outstanding|o (to print all outstanding cards)\n'\
    'show state|s (to show some general game state)\n'\
    'show play|p (to show which cards have been played successfully)\n'\
    'show discard|d (to show which cards are out of play)\n'\
    'show rules|r (to show the current ruleset being used)\n'\
    'show hand|h [player] (to show the hand of [player])\n'\
    '---> [player] can be a number indicating turn order or a\n'\
    '     string which unambiguously identifies the player (defaults to player up).\n'\
    '---> Output displays for each card the round drawn (RD), possible colors,\n'\
    '     round (RU) and turn (TU) last updated, and possible numbers.\n'\
    'show card|c <player> <position> (to show information about a card in <player>\'s hand)\n'\
    'This shows the history of all past states the card has had, and when.\n'\
    '---> <player> can be a number indicating turn order or a\n'\
    '     string which unambiguously identifies the player.\n'\
    'show info|i <option> [sort] (to show statistics about the game so far)\n'\
    '---> For detailed information on show info, use "help show info".\n'\
    'show graph|g <options> (to graph information about the game so far)\n'\
    '---> For detailed information on show graph, use "help show graph".'

SHOW_INFO_TEXT = \
    'The "show" command\'s "info" option.  Used to show statistics about the game so far.\n'\
    'Usage:\n'\
    'show info|i <option> [sort]\n'\
    '---> <option> can be a player or a type of information to be printed.\n'\
    '     If player, must be number or string which unambiguously identifies a player.\n'\
    '     Else, is an option:\n'\
    '     play|p for plays; discard|d for discards; misfire|m for misfires; hint|h for hints\n'\
    '---> [sort] specifies which information to sort by.\n'\
    '     sort options for plays, discards, and misfires:\n'\
    '         round|r for round performed (default);\n'\
    '         player|p for player performing action;\n'\
    '         card|c for card acted upon.\n'\
    '     sort options for hint:\n'\
    '         round|r for round performed (default);\n'\
    '         giver|g for giver of hint;\n'\
    '         target|t for recipient of hint;\n'\
    '         number|n for number of positions hinted;\n'\
    '         hint|h for hint given (color or number).\n'\
    '     sort options for players:\n'\
    '         round|r for round performed (default);\n'\
    '         action|a for action taken.'

SHOW_GRAPH_TEXT = \
    'The "show" command\'s "graph" option.  Used to graph statistics about the game so far.\n'\
    'Usage:\n'\
    'show graph|g <options>\n'\
    '---> <options> can be one of {play|p, discard|d, misfire|m, hint|h} to print\n'\
    '     a graph of percentages of plays/discards/misfires/hints performed by each player.\n'\
    '---> If using the hint option, one can use additional arguments:\n'\
    '         to|> <player> to graph percentages of hints to <player>, by giver;\n'\
    '         from|< <player> to graph percentages of hints from <player>, by destination.'


#The logic for the "show" command
def show_text(choice, game):
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
            try: player = parsing.resolve_player(player, game)
            except HanabiInputException as e: return e.args[0]
            try: position = int(position)
            except ValueError: return f'Expected an integer card position; yours: {position}.'
            if not 1 <= position <= len(player.hand): return f'Position {position} is out of range.'
            text = f'{player.name} card {position}:\n{player.represent_card(position - 1)}'
        case ['card', *args] | ['c', *args]:
            text = 'Additional input required for card history; see "help show"'
        case ['hand', *args] | ['h', *args]:
            if len(args) > 1: return f'Unrecognized arguments {", ".join(args)}; try "help show"'
            try: player_request = args[0]
            except IndexError as e: player_request = game.player_up + 1 #default is player up
            try: player = parsing.resolve_player(player_request, game)
            except HanabiInputException as e: return e.args[0]
            text = str(player)
        case ['rules'] | ['r']:
            text = str(game.rules)
        case ['info', *args] | ['i', *args]:
            match args:
                case ['play', *sort] | ['p', *sort]:
                    actions = game.get_actions_of_type(PlayAction)
                    header = ['index', 'round', 'player', 'card']
                    try: action_metadata = reporting.sort_stats_playdiscardmisfire(actions, sort)
                    except HanabiSimException as e: return e.args[0]
                    rows = [
                        [index + 1, md.round, game.players[md.player].name, md.action.realized]
                        for index, md in enumerate(action_metadata)
                    ]
                    text = tabulate(rows, headers=header, tablefmt='pretty')
                case ['discard', *sort] | ['d', *sort]:
                    actions = game.get_actions_of_type(DiscardAction)
                    header = ['index', 'round', 'player', 'card']
                    try: action_metadata = reporting.sort_stats_playdiscardmisfire(actions, sort)
                    except HanabiSimException as e: return e.args[0]
                    rows = [
                        [index + 1, md.round, game.players[md.player].name, md.action.realized]
                        for index, md in enumerate(action_metadata)
                    ]
                    text = tabulate(rows, headers=header, tablefmt='pretty')
                case ['misfire', *sort] | ['m', *sort]:
                    actions = game.get_actions_of_type(MisfireAction)
                    header = ['index', 'round', 'player', 'card']
                    try: action_metadata = reporting.sort_stats_playdiscardmisfire(actions, sort)
                    except HanabiSimException as e: return e.args[0]
                    rows = [
                        [index + 1, md.round, game.players[md.player].name, md.action.realized]
                        for index, md in enumerate(action_metadata)
                    ]
                    text = tabulate(rows, headers=header, tablefmt='pretty')
                case ['hint', *sort] | ['h', *sort]:
                    actions = game.get_actions_of_type(HintAction)
                    header = ['index', 'round', 'giver', 'receiver', 'cards', 'hint']
                    try: action_metadata = reporting.sort_stats_hints(actions, sort)
                    except HanabiSimException as e: return e.args[0]
                    rows = [
                        [
                            index + 1,
                            md.round,
                            game.players[md.player].name,
                            game.players[md.action.targetplayer_index].name,
                            ', '.join([str(p + 1) for p in md.action.positions]),
                            md.action.hint,
                        ]
                        for index, md in enumerate(action_metadata)
                    ]
                    text = tabulate(rows, headers=header, tablefmt='pretty')
                case [player_request, *sort]:
                    try: player = parsing.resolve_player(player_request, game)
                    except HanabiInputException as e: return e.args[0]
                    actions = game.get_actions_of_player(game.get_player_index(player))
                    header = ['index', 'round', f'{player.name} action']
                    try: actions_metadata = reporting.sort_stats_players(actions, sort)
                    except HanabiSimException as e: return e.args[0]
                    rows = [
                        [
                            i + 1,
                            md.round,
                            f'Played {md.action.realized}'
                            if isinstance(md.action, PlayAction) else
                            f'Discarded {md.action.realized}'
                            if isinstance(md.action, DiscardAction) else
                            f'Misfired {md.action.realized}'
                            if isinstance(md.action, MisfireAction) else
                            f'Hinted {game.players[md.action.targetplayer_index].name} about '
                            f'{md.action.hint} at positions '
                            f'{", ".join([str(p + 1) for p in md.action.positions])}.'
                            if isinstance(md.action, HintAction)
                            else '?!? Should never happen!',
                        ]
                        for i, md in enumerate(actions_metadata)
                    ]
                    #Note: a player's action list is heterogeneous, so 'sort' can only group
                    #by action type; unlike hints/cards, there is no richer field to sort on.
                    #TODO investigate whether this could or should be improved
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
                    action_takers = [game.players[md.player].name for md in actions]
                    #Generate map from names to times taking PlayAction
                    data = {
                        name : len([*filter(lambda x: x == name, action_takers)])
                        for name in [p.name for p in game.players]
                    }
                    title = f'{st} Actions by Player'
                    text = pie_chart.generate_pie_chart(
                        title, data, pie_chart.DEFAULT_CHART_HEIGHT, True
                    )
                case ['hint', 'to',   player] | ['h', 'to',   player] | \
                     ['hint', '>',    player] | ['h', '>',    player] | \
                     ['hint', 'from', player] | ['h', 'from', player] | \
                     ['hint', '<',    player] | ['h', '<',    player] :
                    actions = game.get_actions_of_type(HintAction)
                    try: player_idx = game.get_player_index(player)
                    except HanabiInputException as e: return e.args[0]
                    target = lambda md: md.action.targetplayer_index
                    #filter out hints not from (to) the requested player
                    if args[1] in {'from', '<'}:
                        actions = [md for md in actions if md.player == player_idx]
                    else: actions = [md for md in actions if target(md) == player_idx]
                    #TODO add options to make charts of other facts than just hint giver/receiver
                    #get just the name of the hint giver (receiver)
                    if args[1] in {'to', '>'}:
                        actions = [game.players[md.player].name for md in actions]
                    else: actions = [game.players[target(md)].name for md in actions]
                    #don't put the target player in the chart; he can't hint himself
                    #but do put other players in even if they haven't hinted the target
                    #(or been hinted by the target)
                    target_name = game.get_player(player_idx).name
                    eligible_players = [p.name for p in game.players if p.name != target_name]
                    data = {p : 0 for p in eligible_players} | reporting.unique_counts(actions)
                    st = 'to' if args[1] in {'to', '>'} else 'from'
                    title = f'Hints {st} {game.get_player(player_idx).name}'
                    text = pie_chart.generate_pie_chart(
                        title, data, pie_chart.DEFAULT_CHART_HEIGHT, True
                    )
                case [*args]:
                    text = f'Unrecognized arguments {" ".join(args)}; try "help show graph"'
        case [*args]:
            text = f'Unrecognized arguments: {", ".join(args)}; try "help show".'
    return text


class ShowCommand(Command):

    name = 'show'
    aliases = ('s',)
    accepts_subhelp = True
    help = {
        (): SHOW_TEXT,
        ('info',): SHOW_INFO_TEXT,
        ('i',): SHOW_INFO_TEXT,
        ('graph',): SHOW_GRAPH_TEXT,
        ('g',): SHOW_GRAPH_TEXT,
    }

    def handle(self, options, game):
        return CommandResult(game, show_text(options, game))
