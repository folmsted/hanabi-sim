from tabulate import tabulate
from bisect import insort
from game_objects.color import Color, style_text, guess_text

from game_objects.card import Card, UnknownCard, RealizedCard
from game_objects.card import MIN_CARD_VALUE, MAX_CARD_VALUE, CARD_FREQUENCIES
from game_objects.actions import *
from game_objects.exceptions import HanabiSimException, HanabiRulesException, HanabiIndexException

class Hand:
    """
    A collection of the cards in the hand of a player
    """
    def __init__(self, HAND_SIZE, rules):
         if rules: self.hand = [UnknownCard(0, '-', rules) for _ in range(HAND_SIZE)]

    def process_hint(self, positions, hint, rules, r, t):
        """
        Update all cards in the hand according to a hint given.
        Positions which are given in the hint need to be updated positively
        (setting card values according to the hint), and positions not
        given in the hint need to be updated negatively
        (removing the possibility of having the value or color given in the hint).
        """
        new_hand = self.copy()
        for i, card in enumerate(self.hand):
            if isinstance(hint, Color):
                if hint == Color.MULTICOLOR and not rules['rainbow_enabled']:
                    raise HanabiSimException(f'This game does not have {Color.MULTICOLOR} cards.')
                try: 
                    new_hand.hand[i] = card.hint_color_positive(hint, r, t, rules) if i in positions \
                                       else card.hint_color_negative(hint, r, t, rules)
                except HanabiSimException  as e: raise HanabiIndexException(i, *e.args)
                except HanabiRulesException as e: raise e
            else:
                try:
                    new_hand.hand[i] = card.hint_number_positive(hint, r, t) if i in positions \
                                  else card.hint_number_negative(hint, r, t)
                except HanabiSimException   as e: raise HanabiIndexException(i, *e.args)
                except HanabiRulesException as e: raise e
        return new_hand

    def process_guess(self, position, guess, rules):
        try: card = self.hand[position]
        except IndexError: raise HanabiIndexException(position)
        if isinstance(guess, int):
            if guess not in card.numbers:
                raise HanabiSimException(f'Bad guess; number {guess} already disqualified.')
            new_card_state = card.guess_number(guess)
        elif isinstance(guess, Color):
            if guess == Color.MULTICOLOR and not rules['rainbow_enabled']:
                raise HanabiSimException(f'This game does not have {Color.MULTICOLOR} cards.')
            if guess not in card.colors:
                raise HanabiSimException(f'Bad guess; color {style_text(guess, guess.name)} '
                                         f'already disqualified.')
            new_card_state = card.guess_color(guess)
        new_hand = self.copy()
        new_hand.hand[position] = new_card_state
        return new_hand

    def process_swap(self, index1, index2):
        if not 0 <= index1 < len(self): raise HanabiIndexException(index1)
        if not 0 <= index2 < len(self): raise HanabiIndexException(index2)
        new_hand = self.copy()
        new_hand.hand[index1], new_hand.hand[index2] = new_hand[index2], new_hand[index1]
        return new_hand

    def replace_card(self, cur_round, position, player, rules):
        """
        Remove a card in the hand and replace it according to the player's preferred mode
        of hand organization.
        """
        new_hand = self.copy() 
        match player.replenishment_protocol:
            #Player views his own cards (left to right) as 1, 2, ..., n
            case 'left_shift':
                #If 1 is played, 2 becomes 1, 3 becomes 2, and so on, and the new card is n
                del new_hand.hand[position]
                new_hand.hand.append(UnknownCard(cur_round, player.name, rules))
            case 'right_shift':
                #The new card is 1; if n is played then 1 becomes 2, ... n - 1 becomes n
                del new_hand.hand[position]
                new_hand.hand.insert(0, UnknownCard(cur_round, player.name, rules))
            case 'in_place':
                #The new card takes the place of the old card.  If 3 is played, the new card is 3
                new_hand.hand[position] = UnknownCard(cur_round, player.name, rules)
            case _:
                raise HanabiSimException('Illegal replenishment protocol')
        return new_hand

    def num_possible_states(self):
        accumulator = 1
        for card in self.hand:
            accumulator *= card.num_possible_states()
        return accumulator

    def __len__(self):
        return len(self.hand)

    def __eq__(self, other):
        if not isinstance(other, Hand): return False
        return self.hand == other.hand

    def __getitem__(self, item):
        return self.hand[item]

    def __str__(self):
        colorstrs = [
            ''.join([
                '' if color not in card.colors else
                guess_text(color, color.name[0]) if color == card.color_guess else
                style_text(color, color.name[0], deterministic=True) for color in Color
            ]) for card in self.hand
        ]
        numberstrs = [
            ''.join([
                guess_text(number, str(number)) if number == card.number_guess
                else str(number) for number in card.numbers

            ]) for card in self.hand
        ]
        rounds_drawn        = [f'RD: {card.round_drawn}'   for card in self.hand]
        rounds_last_updated = [f'RU: {card.round_updated}' for card in self.hand]
        turns_last_updated  = [f'TU: {card.turn_updated}'  for card in self.hand]
        rep = tabulate([rounds_drawn,
                       colorstrs,
                       rounds_last_updated,
                       turns_last_updated,
                       numberstrs], \
                       tablefmt='pretty'
        )
        return rep

    def copy(self):
        cpy = Hand(len(self.hand), None)
        cpy.hand = [card for card in self.hand] #UnknownCard immutable; shallow copy safe 
        return cpy


class PlayedCards:
    """
    A collection of cards which have been played successfully, adding to a firework.
    """
    def __init__(self, rules):
        self.cards = {color : Card(color, 0) for color in (Color)}
        #if rainbows do not play into a suit, do not track them
        if not (rules['rainbow_enabled'] and rules['rainbow_play'] == 'suit'):
            del self.cards[Color.MULTICOLOR]
        self.rules = rules

    def add(self, card):
        color = card.color
        if not (self.cards[color].number + 1 == card.number): raise HanabiSimException('')#TODO be more elegant here
        new_state = self.copy()
        new_state.cards[color] = card
        return new_state

    def values(self):
        return self.cards.values()

    def copy(self):
        cpy = PlayedCards(self.rules)
        cpy.rules = self.rules
        cpy.cards = {k : v for k, v in self.cards.items()} #color and Cards immutable
        return cpy

    def __str__(self):
        return tabulate([[self.cards[color] for color in self.cards]],
                        tablefmt = 'pretty')

    def __getitem__(self, key):
        return self.cards[key]
 

class OutstandingCards:
    """
    A collection of all cards in the game of Hanabi.
    Updated throughout the game to exclude cards revealed
    by discards and plays.  Notably, cards which are in players' hands are
    considered to be outstanding because they are not publicly known.
    """
    def __init__(self, rules):
        self.cards = []
        self.rules = rules

        for color in Color:
            #if the game contains no rainbow cards, do not track them
            if color == Color.MULTICOLOR and not self.rules['rainbow_enabled']: continue
            for i in range(MIN_CARD_VALUE, MAX_CARD_VALUE + 1):
                for j in range(CARD_FREQUENCIES[i - 1]):
                   self.cards.append(Card(color, i))

    def remove(self, card):
        copy = self.copy()
        copy.cards.remove(card)
        return copy

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        data = [[style_text(color, color.name) for color in Color \
                 if (color != Color.MULTICOLOR or self.rules['rainbow_enabled'])]]
        #Sort outstanding cards by color
        columns = [ [*filter(lambda card: card.color == color, self.cards)] for color in Color \
                    if (color != Color.MULTICOLOR or self.rules['rainbow_enabled']) ]
        table_length = max([len(col) for col in columns])
        #Create table rows.  Each row is the next card number of that color, or empty if no
        #cards of that color remain.
        for i in range(table_length):
            row = [columns[j][i] if len(columns[j]) >= i + 1 else ' ' 
                   for j in range(len(Color) - (0 if self.rules['rainbow_enabled'] else 1))]
            data.append(row)
        return tabulate(data, headers='firstrow', tablefmt = 'pretty')

    def contains(self, card, count = 1):
        return self.cards.count(card) >= count

    def copy(self):
        cpy = OutstandingCards(self.rules)
        #cards immutable; no deep copy needed
        cpy.cards = self.cards.copy()
        cpy.rules = self.rules
        return cpy


class DiscardedCards:
    """
    A collection of all cards which have been discarded.
    """
    def __init__(self, rules):
        self.cards = {color : [] for color in (Color)}
        #if the game contains no rainbow cards, do not track them
        if not rules['rainbow_enabled']: del self.cards[Color.MULTICOLOR]
        self.rules = rules

    def add(self, card):
        new_state = self.copy()
        insort(new_state.cards[card.color], card, key = lambda c: c.number)
        return new_state

    def copy(self):
        cpy = DiscardedCards(self.rules)
        cpy.cards = {color : lst.copy() for color, lst in self.cards.items()} #shallow copy lists
        cpy.rules = self.rules
        return cpy

    def __str__(self):
        #Have as many rows as needed to fit all the cards of the most-discarded color
        table_length = max([len(l) for l in self.cards.values()])

        header = [style_text(color, color.name) for color in Color \
                  if (color != Color.MULTICOLOR or self.rules['rainbow_enabled'])]
        data = [header]
        for i in range(table_length):
            #Create table rows.  Each row is the next card number of that color, or empty if no
            #cards of that color remain.
            row = [self.cards[color][i] if len(self.cards[color]) >= i + 1 else ' ' \
                   for color in Color \
                   if (color != Color.MULTICOLOR or self.rules['rainbow_enabled'])]
            data.append(row)
        return tabulate(data, headers='firstrow', tablefmt = 'pretty')



