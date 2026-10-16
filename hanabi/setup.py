from hanabi.game_objects.rules import HanabiRuleset
from hanabi.game_objects.game_state import GameState
from hanabi.game_objects.styling import style_text
from hanabi.game_objects.exceptions import HanabiException
from hanabi.parsing import trim_comment, COMMENT_START


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

PLAYERNAME_MAX_LENGTH = 16


def get_rules(setup_choices, outfile, color_picker):
    """
    Prompt the user (or read from file) to establish rules.
    """
    rules = HanabiRuleset()
    done = False
    while (not done):
        rule = setup_choices.pop(0).strip() if setup_choices else input(
            style_text(
                next(color_picker),
                f'Print rules, change a rule, go to game, or ask for help with \'?\':'
            )
        )
        if outfile: outfile.write(rule + '\n')
        rule = trim_comment(rule, COMMENT_START).strip().split()
        match rule:
            case ['?']:
                helpstr = (
                    'To print rules, use "print rules" or just \'p\' for short.\n'
                    'To comfirm current rules and continue, leave blank.\n'
                    'To change a rule, type the rule name or short '
                    'form and the new value to give it.\n'
                    'To explain what a rule does, type "explain <rulename|short form>".\n'
                    'For rules with only two possible values, giving '
                    'no value toggles between options.'
                )
                print(helpstr)
            case []:
                done = True
            case ['print', 'rules'] | ['p']:
                print(rules)
            case ['explain', arg]:
                try: print(rules.get_description(arg))
                except HanabiException as e: print(e.args[0])
            case [rulestr, *arg]:
                if arg and len(arg) > 1:
                    print('Too many arguments; provide just a rule and a value.')
                try: rules.change_rule(rulestr, arg[0] if arg else None)
                except HanabiException as e: print(e.args[0])
    return rules

def get_players(setup_choices, outfile, color_picker):
    """
    Prompt the user (or read from file) to get the players and their preferred
    modes of organizing their hands
    """
    players = []
    protocols = []
    done = False
    while (not done):
        #first, query for a player name
        playername = setup_choices.pop(0).strip() if setup_choices else input(
            style_text(
                next(color_picker),
                f'Enter player {len(players) + 1} name (16 characters max, '
                f'no spaces), or nothing to proceed to game:'
            )
        )
        if outfile: outfile.write(playername + '\n')
        playername = trim_comment(playername, COMMENT_START).strip()
        #check if duplicate player name
        if playername in players:
            print('There is already a player with this name.')
            continue
        #check if name too long
        if len(playername) > PLAYERNAME_MAX_LENGTH:
            print(f'Player names must be no more than 16 characters; yours {len(playername)}.')
            continue
        #check whether any character is whitespace
        if any([c in ' \t\n\r\x0b\x0c' for c in playername]):
            print('Player names must not have any whitespace.')
            continue
        if (not playername and len(players) < GameState.MIN_PLAYERS):
            print(f'The game needs at least {GameState.MIN_PLAYERS} players!')
            continue
        if (not playername): return players, protocols

        #second, query for a replenishment protocol
        invalid = True
        while (invalid):
            protocol = setup_choices.pop(0).strip() if setup_choices else input(
                style_text(
                    next(color_picker),
                    f'Enter the replenishment protocol (in place|left shift|right shift)'
                    f' for player {len(players) + 1} {playername} ("?" for help):'
                )
            )
            if outfile: outfile.write(protocol + '\n')
            protocol = trim_comment(protocol).strip()
            if protocol == '?':
                print(
                    'A player\'s replenishment protocol is how he replaces a card removed from '
                    'his hand.\n"in place" means the new card takes the place of the old one;\n'
                    '"left shift" means that all cards are shifted left as much as possible\n'
                    'and the new card is inserted at the rightmost position; and\n'
                    '"right shift" means that all cards are shifted right as much as possible,\n'
                    'and the new card is inserted at position 1, the leftmost position.\n'
                    'For example, if a player holding 5 cards played his position 3 card:\n'
                    'a left-shifter would move cards 4 and 5 to positions 3 and 4,\n'
                    'and the new card would go in position 5; and\n'
                    'a right-shifter would move cards 1 and 2 to positions 2 and 3,\n'
                    'and the new card would go in position 1; and\n'
                    'an in-place replacer would place the new card in position 3,\n'
                    'and he would move no other cards.'
                )
                continue
            try:
                protocols.append(PROTOCOL_MAP[protocol.lower()])
                players.append(playername)
                invalid = False
            except KeyError: pass
        if len(players) == GameState.MAX_PLAYERS:
            print('The maximum number of players has been reached!')
            done = True
    return players, protocols
