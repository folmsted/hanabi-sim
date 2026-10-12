from hanabi import parsing
from hanabi.game_objects.color import Color
from hanabi.game_objects.styling import style_text

from hanabi.game_objects.exceptions import (
    HanabiException, HanabiIndexException, HanabiInputException,
    HanabiUserInputRequiredException,
)


#The logic for the "play" command
def handle_play(choice, game, verbose=False):
    match choice:
        case [position, card]:
            pass #do nothing, the case statement extracts the values for us
        case [position, card, *args]:
            return game, f'Unrecognized arguments: {", ".join(args)}; try "help play"'
        case [*args]:
            return game, 'This command requires additional input; try "help play"'
    try: card = parsing.read_card(card)
    except HanabiInputException as e: return game, e.args[0]
    try: position = int(position)
    except ValueError as e: return game, f'The specified position ({position}) is not an integer.'
    player = game.get_player(game.player_up)
    try: new_state = player.perform_play(position - 1, card, game, verbose=verbose)
    except HanabiIndexException as e: return game, f'Card {e.index + 1}: {e.args[0]}'
    #We must kick this one upstairs; we cannot (cleanly) poll the user here
    except HanabiUserInputRequiredException as e: raise e
    except HanabiException as e: return game, e.args[0]
    return new_state, 'Success; advancing turn'

#The logic for the "play" command after the user plays a rainbow card in wild-play
#mode and has supplied the choice of (valid) color to which the card will apply
def handle_wild_play(e_args, game, setup_choices, outfile, color_picker, verbose):
    colors, card, position, table = e_args
    #Get the user to select a color to apply to the card
    print(table)
    prompt = 'Select from the above table to which color firework this card applies:'
    try: choice = setup_choices.pop(0).strip() if setup_choices else \
                  input(style_text(next(color_picker), prompt))
    except (KeyboardInterrupt, EOFError):
        print('Program terminated by user.')
        exit(0)
    if outfile: outfile.write(choice + '\n')

    #valid colors are at least 1 and at most 5, by construction, since there are
    #only ever 5, not 6 suits in wild-play mode because rainbow is not a suit.
    #Therefore we can reuse this function.
    try: choice = parsing.read_color_or_number(choice)
    except HanabiInputException as e: return game, e.args[0]
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
    except HanabiIndexException as e: return game, f'Card {e.index + 1}: {e.args[0]}'
    except HanabiException as e: return game, e.args[0]
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
            return game, (
                f'Could not find a player {target_player}; '
                f'total players: {game.num_players}'
            )
        target_player = target_player - 1
    except ValueError:
        #player given by name
        target_player = choice[0]
    try: target_player = game.get_player(target_player)
    except HanabiInputException as e: return game, e.args[0]
    #resolve hint
    try: hint = parsing.read_color_or_number(hint)
    except HanabiInputException as e: return game, e.args[0]
    #resolve positions
    if (not positions): return game, 'You must specify positions to hint to.'
    try:
        #correction for convention of 1-indexed cards
        positions = [int(p) - 1 for p in positions]
    except ValueError:
        return game, f'Your indicated positions {", ".join(positions)} were not all integers.'
    #do the hint
    try: new_state = player.perform_hint(target_player, positions, hint, game, verbose=verbose)
    except HanabiIndexException as e: return game, f'Position {e.index + 1}: {e.args[0]}'
    except HanabiException as e: return game, e.args[0]
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
    try: card = parsing.read_card(card)
    except HanabiInputException as e: return game, e.args[0]
    try: position = int(position)
    except ValueError as e: return game, f'The specified position ({position}) is not an integer.'
    player = game.get_player(game.player_up)
    try: new_state = player.perform_discard(position - 1, card, game, verbose=verbose)
    except HanabiIndexException as e: return game, f'Card {e.index + 1}: {e.args[0]}'
    except HanabiException as e: return game, e.args[0]
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
    try: player = parsing.resolve_player(player, game)
    except HanabiInputException as e: return game, e.args[0]
    try: guess = parsing.read_color_or_number(guess)
    except HanabiInputException as e: return game, e.args[0]
    try: position = int(position)
    except ValueError: return game, f'Invalid position; expected number 1 to 5; yours: {position}'
    #apply the guess
    try: new_state = player.perform_guess(position - 1, guess, game, verbose=verbose)
    except HanabiIndexException as e: return game, f'Card {e.index + 1}: {e.args[0]}'
    except HanabiException as e: return game, e.args[0]
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
    try: player = parsing.resolve_player(player, game)
    except HanabiInputException as e: return game, e.args[0]
    try: index1, index2 = int(index1), int(index2)
    except ValueError: return game, f'Integers expected as indices; yours: {index1, index2}'
    try: new_state = player.perform_swap(index1 - 1, index2 - 1, game, verbose=verbose)
    except HanabiIndexException as e: return game, f'Card {e.index + 1}: {e.args[0]}'
    except HanabiException as e: return game, e.args[0]
    return new_state, 'Success'
