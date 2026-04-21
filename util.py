from game_objects import *
from pie_chart import generate_pie_chart, DEFAULT_CHART_HEIGHT
import random
import readline
import argparse
from enum import Enum


PROTOCOL_MAP = {
    'i'           : 'in_place',
    'in'          : 'in_place',
    'in place'    : 'in_place',
    'in_place'    : 'in_place',

    'l'           : 'left_shift',
    'left'        : 'left_shift',
    'left shift'  : 'left_shift',
    'left_shift'  : 'left_shift',

    'r'           : 'right_shift',
    'right'       : 'right_shift',
    'right shift' : 'right_shift',
    'right_shift' : 'right_shift'
}

COMMENT_START = '//'
PLAYERNAME_MAX_LENGTH = 16


def get_color_from_str(s):
    match s:
        case s if 'blue'      .startswith(s.lower()): return Color.BLUE
        case s if 'green'     .startswith(s.lower()): return Color.GREEN
        case s if 'red'       .startswith(s.lower()): return Color.RED
        case s if 'white'     .startswith(s.lower()): return Color.WHITE
        case s if 'yellow'    .startswith(s.lower()): return Color.YELLOW
        case s if 'multicolor'.startswith(s.lower()): return Color.MULTICOLOR
        #'r' maps to red not rainbow
        case s if 'rainbow'   .startswith(s.lower()): return Color.MULTICOLOR
        case _ : raise KeyError(f'Input {s} does not correspond to any color.')
        
def trim_comment(string, comment_delimiter=COMMENT_START):
    """
    Search for any part of a string which comes after the given comment_delimiter
    Return a string which omits this portion.
    """
    x = string.find(comment_delimiter)
    return string if x == -1 else string[:x]

def get_rules(setup_choices, outfile, color_picker):
    """
    Prompt the user (or read from file) to establish rules.
    """
    rules = HanabiRuleset()
    done = False
    while (not done):
        rule = setup_choices.pop(0).strip() if setup_choices else \
                     input(style_text(next(color_picker),
                           f'Print rules, change a rule, go to game, or ask for help with \'?\':'
                     ))
        if outfile:
            outfile.write(rule + '\n')
        rule = trim_comment(rule, COMMENT_START).strip().split()
        match rule:
            case ['?']:
                helpstr = \
                    'To print rules, use "print rules" or just \'p\' for short.\n'\
                    'To comfirm current rules and continue, leave blank.\n'\
                    'To change a rule, type the rule name or short '\
                    'form and the new value to give it.\n'\
                    'To explain what a rule does, type "explain <rulename|short form>".\n'\
                    'For rules with only two possible values, giving '\
                    'no value toggles between options.'
                print(helpstr)
            case []:
                done = True
            case ['print', 'rules'] | ['p']:
                print(rules)
            case ['explain', arg]:
                try:
                    print(rules.get_description(arg))
                except KeyError as e: print(e.args)
                except Exception as e: raise e
            case [rulestr, *arg]:
                if arg and len(arg) > 1:
                    print('Too many arguments; provide just a rule and a value.')
                try: rules.change_rule(rulestr, arg[0] if arg else None)
                except (HanabiSimException, HanabiRulesException) as e: print(e.args[0])
                #except TypeError as e: print('Aditional input required.')
                except HanabiRulesException as e: print(e.args[0])
    return rules

def get_players(setup_choices, outfile, color_picker):
    """
    Prompt the user (or read from file) to get the players and their preferred
    mode of organizing their hands
    """
    players = []
    protocols = []
    done = False
    while (not done):
        playername = setup_choices.pop(0).strip() if setup_choices else \
                     input(style_text(next(color_picker),
                           f'Enter player {len(players) + 1} name (16 characters max, '\
                           f'no spaces), or nothing to proceed to game:'
                     ))
        if outfile:
            outfile.write(playername + '\n')
        playername = trim_comment(playername, COMMENT_START).strip()
        #check if name too long
        if len(playername) > PLAYERNAME_MAX_LENGTH:
            print(f'Player names must be no more than 16 characters; yours {len(playername)}.')
            continue
        #check whether any character is whitespace
        if True in [c in ' \t\n\r\x0b\x0c' for c in playername]:
            print('Player names must not have any whitespace.')
            continue
        if (not playername and len(players) < GameState.MIN_PLAYERS):
            print(f'The game needs at least {GameState.MIN_PLAYERS} players!')
            continue
        if (not playername):
            return players, protocols

        invalid = True
        while (invalid):
            protocol = setup_choices.pop(0).strip() if setup_choices else \
                       input(style_text(next(color_picker),\
                           f'Enter the replenishment protocol (in place|left shift|right shift)'\
                           f' for player {len(players) + 1} {playername} ("?" for help):'))
            if outfile:
                outfile.write(protocol + '\n')
            protocol = trim_comment(protocol).strip()
            if protocol == '?':
                print(
                    'A player\'s replenishment protocol is how he replaces a card removed from '\
                    'his hand.\n"in place" means the new card takes the place of the old one;\n'\
                    '"left shift" means that all cards are shifted left as much as possible\n'\
                    'and the new card is inserted at the rightmost position; and\n'\
                    '"right shift" means that all cards are shifted right as much as possible,\n'\
                    'and the new card is inserted at position 1, the leftmost position.\n'\
                    'For example, if a player holding 5 cards played his position 3 card:\n'\
                    'a left-shifter would move cards 4 and 5 to positions 3 and 4,\n'\
                    'and the new card would go in position 5; and\n'\
                    'a right-shifter would move cards 1 and 2 to positions 2 and 3,\n'\
                    'and the new card would go in position 1; and\n'\
                    'an in-place replacer would place the new card in position 3,\n'\
                    'and he would move no other cards.'
                )
                continue
            try:
                protocols.append(PROTOCOL_MAP[protocol.lower()])
                players.append(playername)
                invalid = False
            except:
                pass
        if len(players) == GameState.MAX_PLAYERS:
            print('The maximum number of players has been reached!')
            done = True
    return players, protocols

#A generator to randomly shuffle some reasonably legible colors and return them in that order forever, repeating when exhausted.
def generate_color():
    #Commented colors are harder to read; move pound signs to include additional colors 
    colors =  ([
                  Fore.RED, Fore.GREEN, Fore.YELLOW, #Fore.BLACK,
                  Fore.MAGENTA, Fore.BLUE, Fore.CYAN, #Fore.WHITE,
                  Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX, #Fore.LIGHTBLACK_EX
                  Fore.LIGHTYELLOW_EX, Fore.LIGHTBLUE_EX,
                  Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX, #Fore.LIGHTWHITE_EX
              ])
    random.shuffle(colors)

    i = 0
    while (i < len(colors)):
        yield colors[i]
        i = (i + 1) % len(colors)

def read_card(s):
    """
    Given a user-inputted string representing a card, (specifying number and color),
    return a Card object with the specified values or error correctly
    """
    n = -1
    c = None
    try:
        n = int(s[0])
        c = get_color_from_str(s[1:])
    except:
        try:
            n = int(s[-1])
            c = get_color_from_str(s[:-1])
        except:
            raise ValueError(f'You must specify a number and color; your input: {s}')
    if not (1 <= n <= 5):
        raise ValueError(f'Illegal number ({n}) given.')
    if not isinstance(c, Color):
        raise ValueError(f'Illegal color ({c}) given.')
    return Card(c, n)

def read_color_or_number(user_input):
    """
    Given a user-inputted string, which should specify a single color or number,
    (but not both), return the associated integer value or Color or error correctly.
    """
    try: 
        ret = int(user_input)
        if not 1 <= ret <= 5: raise ValueError
    except ValueError:
        try:
            ret = get_color_from_str(user_input)
        except KeyError:
            raise HanabiSimException(f'Invalid value; expected number or color; yours: {user_input}')
    return ret

#Given possibly bad user input, return the corresponding player or error correctly
def resolve_player(choice, game):
    try:
        #See if the input is an integer in closed interval [1, num_players]; convert to list index
        player_request = int(choice) - 1
        if player_request < 0:
            raise IndexError(f'Select a player by entering a positive integer; yours: {player_request + 1}')
    except ValueError:
        #Otherwise, assume the value is a player name in the form of a string
        player_request = choice
    try:
        player = game.get_player(player_request)
    except IndexError as e:
        raise IndexError(f'There is no player {player_request + 1}; number of players: {game.num_players}')
    except KeyError as e:
        raise KeyError(e.args[0])
    return player

ActionMetadata = namedtuple('ActionMetadata', ['rnd', 'player', 'action'])

def sort_stats_playdiscardmisfire(actions, sort):
    #package the metadata up in a nice object for sorting
    actions_metadata = [ActionMetadata(a[0], a[1], a[2]) for a in actions]
    if not sort: return actions_metadata
    if len(sort) > 1: raise HanabiSimException(f'Unrecognized options "{" ".join(sort)}".')
    sort = sort[0]
    #define a function for sorting the actions according to requested sort field
    key = lambda metadata: metadata.rnd         if  'round'.startswith(sort) else \
                           metadata.player      if 'player'.startswith(sort) else \
                           metadata.action.card if   'card'.startswith(sort) else \
                           0 #default to no sorting if nothing matches
    try: actions_metadata.sort(key = key)
    except: raise HanabiSimException(f'Unrecognized options "{" ".join(sort)}".')
    return actions_metadata

def sort_stats_hints(actions, sort):
    #package the metadata up in a nice object for sorting
    actions_metadata = [ActionMetadata(a[0], a[1], a[2]) for a in actions]
    if not sort: return actions_metadata
    if len(sort) > 1: raise HanabiSimException(f'Unrecognized options "{" ".join(sort)}".')
    sort = sort[0]
    #If sorting by hint is requested, we sort by number hints first then color hints
    #second.  Since hints are either an int (1-5) or a Color, we cannot compare them
    #directly, so we take numbers at face value (1-5) and Colors as their enum value
    #(1-6) PLUS the total number of Colors (6) so that Colors hints get a higher
    #value than number hints and so are sorted last in the list, as desired.
    key = lambda metadata:                                                              \
        metadata.rnd                          if 'round'.startswith(sort.lower())  else \
        metadata.player                       if 'giver'.startswith(sort.lower())  else \
        metadata.action.targetplayer_index    if 'target'.startswith(sort.lower()) else \
        len(metadata.action.positions)        if 'number'.startswith(sort.lower()) else \
        metadata.action.hint if isinstance(metadata.action.hint, int) else \
        metadata.action.hint.value + len(Color)                            \
                                              if  'hint'.startswith(sort.lower())  else \
        0 #default to no sorting if nothing matches
        

    try: actions_metadata.sort(key=key)
    except: raise HanabiSimException(f'Unrecognized options "{" ".join(sort)}".')
    return actions_metadata

#TODO add options for sorting a player's action... or resolve not to
def sort_stats_players(actions, sort):
    #give a dummy string for player; we don't care about it
    actions_metadata = [ActionMetadata(a[0], '', a[1]) for a in actions]
    if not sort: return actions_metadata
    if len(sort) > 1: raise HanabiSimException(f'Unrecognized options "{" ".join(sort)}".')
    sort = sort[0]
    #Just separate the different action types for now
    key = lambda metadata: \
        isinstance(metadata.action, HintAction)    * 1 + \
        isinstance(metadata.action, PlayAction)    * 2 + \
        isinstance(metadata.action, DiscardAction) * 3 + \
        isinstance(metadata.action, MisfireAction) * 4
    if 'action'.startswith(sort.lower()): actions_metadata.sort(key = key)
    return actions_metadata
    

#help strings.  Moved here because they are unruly and ugly
help_general = \
    'Possible commands (full|shortcut):\nabout|a, help|?, show|s, '\
    'play|p, hint|h, discard|d, guess|g, undo|u, swap, quit|q\n'\
    'Call hint with these arguments for more information on format.'

help_about = \
    'This is hanabi-sim, a simulator for the public information '\
    'available in a game of Hanabi.\n'\
    'This tool tracks all the information which would be available '\
    'to a person with the following properties:\n'\
    '1) He hears all hints given, and knows the givers and recipients\n'\
    '2) He knows the identities of all cards discarded and played, '\
    'and the composition of the Hanabi deck\n'\
    '3) He does NOT see the cards of any player; what he knows about'\
    'hands is purely by hint information\n'\
    '4) He has perfect memory of what he has seen and heard\n'\
    'By inputting to hanabi-sim the moves in a game of Hanabi, '\
    'including the hints, plays, and discards,\n'\
    'you should be able to access all information you know about '\
    'your own hand, and all the information which\n'\
    'your partners know about their hands.  Use the "help" command '\
    'for more specific information on usage.'

help_help = \
    'The "help" command, short form "?".  You can call help with'\
    ' a command after to get extra information.\n'\
    'Examples:\n'\
    'help s (for help on the "show" command)\n'\
    'help hint (for help on the "hint" command)'

help_show = \
    'The "show" command, short form "s".  Used to print information.\n'\
    'Usages:\n'\
    'show outstanding|o (to print all outstanding cards)\n'\
    'show state|s (to show some general game state)\n'\
    'show play|p (to show which cards have been played successfully)\n'\
    'show discard|d (to show which cards are out of play)\n'\
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
    '---> For detailed information on show info, use "help show info".'

help_show_info = \
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

help_play = \
    'The "play" command, short form "p".  '\
    'Used to indicate that turn player should play a card.\n'\
    'Usage:\n'\
    'play <position> <card>\n'\
    'This causes the turn player to play his card in position <position> of his hand.\n'\
    '---> <card> is a value which indicates what value the card had on being revealed.\n'\
    '---> <card> is formatted as <color><number> or <number><color>; '\
    'one-letter abbreviations allowed.\n'\
    'Examples:\n'\
    'play 1 1y (player plays card in position 1, which was a yellow 1)\n'\
    'play 5 3green (player plays card in position 3, which was a green 3)\n'\
    'play 2 r1 (player plays card in position 2, which was a red 1)'

help_hint = \
    'The "hint" command, short form "h".  Used to indicate\n'\
    'that the turn player should give a hint to another player.\n'\
    'Usage:\n'\
    'hint <player> <positions> <hint>\n'\
    'This causes the hand of <player> to be updated '\
    'according to the <hint> for <positions>.\n'\
    '---> <player> can be a number indicating turn order or a\n'\
    '     string which unambiguously identifies the player by name.\n'\
    '---> <positions> is a space-separated list of numbers\n'\
    '     indicating the postions at which to apply the <hint>.\n'\
    '---> <hint> is a number or a string (not both) representing\n'\
    '     the color or number being indicated.\n'\
    'Examples:\n'\
    'hint 1 1 3 4 r (player 1 has red cards at positions 1, 3, 4)\n'\
    'hint fra 2 5 (the player whose name starts "fra" has a 5 at position 2)\n'\
    'hint janos 1 2 3 red (player janos has red cards at positions 1, 2, 3)\n'\
    'hint 2 4 5 2 (player 2 has a two card at positions 4, 5)'

help_discard = \
    'The "discard" command, short form "d".  Used to '\
    'indicate that turn player should discard a card.\n'\
    'Usage:\n'\
    'discard <position> <card>\n'\
    'This causes the turn player to discard his card '\
    'in position <position> of his hand.\n'\
    '---> <card> is a value which indicates what value the card had on being revealed.\n'\
    '---> <card> is formatted as <color><number> or '\
    '<number><color>; abbreviations allowed.\n'\
    'Examples:\n'\
    'discard 1 1y (player discards card in position 1, which was a yellow 1)\n'\
    'discard 5 3green (player discards card in position 3, which was a green 3)\n'\
    'discard 2 r1 (player discards card in position 2, which was a red 1)'

help_guess = \
    'The "guess" command, short form "g".  Used to '\
    'guess the number or color or a card.\n'\
    'Usage:\n'\
    'guess <player> <position> <guess>\n'\
    'This causes the card at <position> in the hand of <player> to be '\
    'updated according to <guess>.\n'\
    'Note that this does not advance play; it is just '\
    'a way to keep track of thoughts.\n'\
    '---> <player> can be a number indicating turn order or a\n'\
    '     string which unambiguously identifies the player by name.\n'\
    '---> <position> is a number indicating the postion \n'\
    '     at which to apply <guess>.\n'\
    '---> <guess> is a number or a string (not both) '\
    'representing the color or number being indicated.\n'\
    'Examples:\n'\
    'guess 1 4 g (player 1 guesses a green card is at position 4)\n'\
    'guess jim 2 5 (the player whose name starts "jim" guesses a 5 is at position 2)\n'\
    'guess janos 3 red (player janos guesses a red card is at position 3)\n'\
    'guess 0 1 2 (player 0 guesses a 2 is at position 1)'

help_undo = \
    'The "undo" command, short form "u".  Used to revert to the previous game state.\n'\
    'Usage:\n'\
    'undo'

help_swap = \
    'The "swap" command (no short form).  Used to '\
    'swap the positions of two cards in a player\'s hand.\n'\
    'Usage:\n'\
    'swap <player> <position1> <position2>\n'\
    'This causes the card at position <position1> to be placed into <position2>.\n'\
    ' and the card in <position2> to be placed in <position1>\n'\
    'Note that this does not advance play; it just '\
    'changes the order of cards in the hand.\n'\
    '---> <player> can be a number indicating turn order or a\n'\
    '     string which unambiguously identifies the player by name.\n'\
    '---> <position1> and <position2> are integers indicating\n'\
    '     the positions of the cards to swap.\n'\
    'Examples:\n'\
    'swap 1 4 5 (player 1 swaps the cards at positions 4 and 5)\n'\
    'swap sigismund 2 5 (the player whose name starts "sigismund" '\
    'swaps the cards at positions 2 and 5)'

help_quit = \
    'The "quit" command, short form "q".  Used to quit the simulation.\n'\
    'Usage:\n'\
    'quit'
 
