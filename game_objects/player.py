from tabulate import tabulate
from game_objects.color import Color

from game_objects.card import Card, RealizedCard
from game_objects.card import MAX_CARD_VALUE
from game_objects.card_collections import Hand

from game_objects.actions import HintAction, DiscardAction, PlayAction, MisfireAction
from game_objects.exceptions import (
    HanabiIndexException, HanabiRulesException,
    HanabiSimException, HanabiUserInputRequiredException,
)

class Player:
    """
    A player in the game of Hanabi, who holds a hand and performs actions to advance the game.
    """
    def __init__(self, name, hand_size, rules, replenishment_protocol='in_place'):
        self.name = name
        if rules: self.hand = Hand(hand_size, rules)
        self.replenishment_protocol = replenishment_protocol

    def perform_discard(self, position, card, game, verbose=False):
        """
        Attempt to perform a discard, updating state of the discarded cards, hints,
        and hand of the player performing the discard.
        """
        if (game.hints >= game.MAX_HINTS):
            raise HanabiRulesException('Cannot discard while hints are at maximum!')
        if (not 0 <= position < len(self.hand)):
            errstr = 'the position given was not in range.\n'\
                     f'Expected an integer between 1 and {len(self.hand)}, inclusive.'
            raise HanabiIndexException(position, errstr)
        if card.color == Color.MULTICOLOR and not game.rules['rainbow_enabled']:
            raise HanabiSimException(f'This game has no {Color.MULTICOLOR} cards.')
        if card.color  not in self.hand[position].colors or\
           card.number not in self.hand[position].numbers:
            errstr = f'The card identity {card} which you gave was not possible '\
                     f'given its possible states.\nThe card:\n{str(self.hand[position])}'
            raise HanabiIndexException(position, errstr)
        new_state = game.copy()
        new_state.hints += 1
        #Put the card in the discard pile for its color; keep the pile sorted numerically
        new_state.discard = new_state.discard.add(card)
        new_state.turns_taken.append(DiscardAction(RealizedCard(card, self.hand[position])))
        try: new_state.outstanding_cards = new_state.outstanding_cards.remove(card)
        except ValueError:
            errstr = f'The card you specified, {card}, is exhausted '\
                     f'by prior plays and discards. (see "show outstanding")'
            raise HanabiSimException(errstr)
        #Replenishment
        new_player = self.copy()
        if (new_state.num_in_deck > 0):
            new_state.num_in_deck -= 1
            new_player.hand = new_player.hand.replace_card(new_state.round, position, self, game.rules)
        else:
            del new_player.hand.hand[position]
        new_state.previous_state = game
        new_state.players[game.player_up] = new_player
        new_state.advance_turn()
        if verbose: print(str(new_player))
        return new_state

    def perform_play(self, position, card, game, verbose=False):
        """
        Attempt to perform a play, updating the played cards or discarded cards (as applicable)
        and the hand of the player performing the discard.
        """
        if (not 0 <= position < len(self.hand)):
            errstr = 'the position you specified was not in range.\n'\
                     f'Expected an integer between 1 and {len(self.hand)}, inclusive.'
            raise HanabiIndexException(position, errstr)
        if card.color == Color.MULTICOLOR and not game.rules['rainbow_enabled']:
            raise HanabiSimException(f'This game has no {Color.MULTICOLOR} cards.')
        if card.color not in self.hand[position].colors or \
           card.number not in self.hand[position].numbers:
            errstr = f'The card identity {card} which you gave was not possible '\
                     f'given its possible states.\nThe card:\n{str(self.hand[position])}'
            raise HanabiIndexException(position, errstr)
        new_state = game.copy()
        try: new_state.outstanding_cards = new_state.outstanding_cards.remove(card)
        except ValueError:
            errstr = f'The card you specified, {card}, is exhausted '\
                     f'by prior plays and discards.  See "show outstanding".' 
            raise HanabiSimException(errstr)

        #user must choose which suit wild rainbow will count as, if any is possible
        if card.color == Color.MULTICOLOR and game.rules['rainbow_play'] == 'wild':
            valid_colors = [c.color for c in game.play.values() if c.number + 1 == card.number]
            #no possible colors to play to; misfire
            if not valid_colors:
                new_state.turns_taken.append(MisfireAction(RealizedCard(card, self.hand[position])))
                new_state.misfires += 1
                new_state.over = new_state.misfires > new_state.MAX_MISFIRES
                if game.rules['bombs_give_hints']:
                    new_state.hints += 1 if new_state.hints < new_state.MAX_HINTS else 0
                new_state.discard = new_state.discard.add(card)
            #possible colors; kick this upstairs to get user to decide
            else:
                table = tabulate(
                    [[i + 1, color] for i, color in enumerate(valid_colors)],
                    tablefmt='pretty'
                )
                raise HanabiUserInputRequiredException(valid_colors, card, position, table)
        else: #card.color != Color.MULTICOLOR or game.rules['rainbow_play'] == 'suit'
            #successful play
            if (card.number == new_state.play[card.color].number + 1):
                new_state.turns_taken.append(PlayAction(RealizedCard(card, self.hand[position])))
                new_state.play = new_state.play.add(card)
                if card.number == MAX_CARD_VALUE:
                    new_state.hints += 1 if new_state.hints < new_state.MAX_HINTS else 0
                    if all([c.number == MAX_CARD_VALUE for c in new_state.play.values()]):
                        new_state.over = True
            #unsuccessful play
            else:
                new_state.turns_taken.append(MisfireAction(RealizedCard(card, self.hand[position])))
                new_state.misfires += 1
                new_state.over = new_state.misfires > new_state.MAX_MISFIRES
                if game.rules['bombs_give_hints']:
                    new_state.hints += 1 if new_state.hints < new_state.MAX_HINTS else 0
                new_state.discard = new_state.discard.add(card)
        #replenish in any event
        new_player = self.copy()
        if (new_state.num_in_deck > 0):
            new_state.num_in_deck -= 1
            new_player.hand = new_player.hand.replace_card(new_state.round, position, self, game.rules)
        else:
            del new_player.hand.hand[position]
        new_state.previous_state = game
        new_state.players[game.player_up] = new_player
        new_state.advance_turn()
        if verbose: print(str(new_player))
        return new_state

    def perform_wild_play(self, position, card, color_choice, game, verbose=False):
        """
        Perform a play action for a game which has rainbow cards set to wild play mode.
        """
        #TODO user input
        new_state = game.copy()
        #import pdb; pdb.set_trace()
        realized_identity = Card(color_choice, card.number)
        realized = RealizedCard(realized_identity, self.hand[position], was_rainbow=True)
        new_state.turns_taken.append(PlayAction(realized))
        #add to the chosen color's play; consider the rainbow card discarded
        new_state.play = new_state.play.add(realized_identity)
        new_state.discard = new_state.discard.add(card)
        new_state.outstanding_cards = new_state.outstanding_cards.remove(card)
        if card.number == MAX_CARD_VALUE:
            new_state.hints += 1 if new_state.hints < new_state.MAX_HINTS else 0
            if all([c.number == MAX_CARD_VALUE for c in new_state.play.values()]):
                new_state.over = True
        new_player = self.copy()
        if (new_state.num_in_deck > 0):
            new_state.num_in_deck -= 1
            new_player.hand = new_player.hand.replace_card(new_state.round, position, self, game.rules)
        else:
            del new_player.hand.hand[position]
        new_state.previous_state = game
        new_state.players[game.player_up] = new_player
        new_state.advance_turn()
        if verbose: print(str(new_player))
        return new_state

    def perform_hint(self, target_player, positions, hint, game, verbose=False):
        """
        Attempt to perform a hint, updating the game state and the hand of the hinted player.
        """
        if game.hints <= 0:
            raise HanabiRulesException('Cannot give a hint while no hints remain!')
        if self == target_player:
            raise HanabiRulesException('One cannot give a hint to oneself!')
        if (not (isinstance(hint, int) or isinstance(hint, Color))):
            raise HanabiSimException(f'Invalid hint given: {hint}')
        if not positions: raise HanabiSimException(f'You must specify the positions hinted.')
        for position in positions:
            if not 0 <= position < len(target_player.hand):
                errstr = f'no such card; position out of range.\n' \
                         f'Expected integer between 1 and {len(target_player.hand)}, inclusive.'
                raise HanabiIndexException(position, errstr)
        if len(positions) != len(set(positions)):
            raise HanabiSimException('Duplicate positions specified.')

        new_state = game.copy()
        new_state.hints -= 1
        new_state.previous_state = game
        new_player = target_player.copy()
        try:
            new_player.hand = new_player.hand.process_hint(
                                  positions, hint, game.rules, new_state.round, self.name)
        except (HanabiIndexException, HanabiSimException) as e: raise e
        new_state.players[game.players.index(target_player)] = new_player
        new_state.advance_turn()
        hint = HintAction(game.players.index(target_player), hint,\
                          positions, target_player.hand, new_player.hand)
        new_state.turns_taken.append(hint)
        if verbose: print(str(new_player))
        return new_state

    #TODO guess functionality may not be in line with the intended use of hanabi-sim
    #decide whether it should be disabled
    def perform_guess(self, position, guess, game, verbose=False):
        """
        Apply the player's guess of color or number to a card.
        This does not consume a player's turn; it just updates the card with the guess.
        """
        if not isinstance(position, int) or not (0 <= position < len(self.hand)):
            raise HanabiIndexException(position, f'Invalid position given.')
        new_state = game.copy()
        new_player = self.copy()
        try: new_player.hand = new_player.hand.process_guess(position, guess, game.rules)
        except (HanabiSimException, HanabiIndexException) as e: raise e
        new_state.players[game.players.index(self)] = new_player
        new_state.previous_state = game
        if verbose: print(str(new_player))
        return new_state

    def perform_swap(self, pos1, pos2, game, verbose=False):
        """
        Swap two cards in a players hand.
        This does not consume the player's turn; it just updates the order
        in which a player's cards appear.
        """
        if not isinstance(pos1, int) or not isinstance(pos2, int):
            raise ValueError(f'integers expected; got {pos1, pos2}')
        if not (0 <= pos1 < len(self.hand)):
            errstr = f'nonnegative integers not exceeding hand size '\
                     f'expected; hand size: {len(self.hand)}.'
            raise HanabiIndexException(pos1, errstr)
        if not (0 <= pos2 < len(self.hand)):
            errstr = f'nonnegative integers not exceeding hand size '\
                     f'expected; hand size: {len(self.hand)}.'
            raise HanabiIndexException(pos2, errstr)
        if pos1 == pos2:
            raise HanabiSimException(f'Identical integers given; no swap to make.')

        new_state = game.copy()
        new_player = self.copy()
        try: new_player.hand = new_player.hand.process_swap(pos1, pos2)
        except HanabiIndexException as e: raise e
        new_state.players[game.players.index(self)] = new_player
        new_state.previous_state = game
        if verbose: print(str(new_player))
        return new_state

    def copy(self):
        cpy = Player(self.name, 0, None, self.replenishment_protocol)
        cpy.hand = self.hand.copy()
        return cpy

    def __str__(self):
        return str(f'{self.name}:\n{self.hand}')

    def represent_card(self, position):
        """
        Show a card in all the states it has held over time, up to and including now.
        """
        fake_hand = Hand(0, None) #we want Hand's formatting for a sequence of card states
        fake_hand.hand = [*self.hand[position].previous_states, self.hand[position]]
        return str(fake_hand)
