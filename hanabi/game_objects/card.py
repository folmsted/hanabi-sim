from tabulate import tabulate
from hanabi.game_objects.color import Color
from hanabi.game_objects.styling import style_text, guess_text
from hanabi.game_objects.exceptions import HanabiSimException, HanabiRulesException

MIN_CARD_VALUE = 1
MAX_CARD_VALUE = 5
CARD_FREQUENCIES = [3,2,2,2,1]


class Card:
    """
    A card of known number and color.
    """
    def __init__(self, color, number):
        self.color = color
        self.number = number

    def __str__(self):
        return style_text(self.color, f'{self.color.name} {self.number}')

    def __repr__(self):
        return style_text(self.color, f'{self.color.name} {self.number}')

    def __eq__(self, other):
        if not isinstance(other, Card): return False
        return self.color == other.color and self.number == other.number

    def __lt__(self, other):
        if not isinstance(other, Card):
            raise ValueError(f'Cannot compare Card {self} and non-card {other}.')
        return self.color.value  * len(Color) + self.number < \
               other.color.value * len(Color) + other.number

    def __gt__(self, other):
        if not isinstance(other, Card):
            raise ValueError(f'Cannot compare Card {self} and non-card {other}.')
        return self.color.value  * len(Color) + self.number > \
               other.color.value * len(Color) + other.number

    def __le__(self, other):
        if not isinstance(other, Card):
            raise ValueError(f'Cannot compare Card {self} and non-card {other}.')
        return self.color.value  * len(Color) + self.number <= \
               other.color.value * len(Color) + other.number

    def __ge__(self, other):
        if not isinstance(other, Card):
            raise ValueError(f'Cannot compare Card {self} and non-card {other}.')
        return self.color.value  * len(Color) + self.number >= \
               other.color.value * len(Color) + other.number

    def copy(self):
        return self


class UnknownCard:
    """
    A card whose identity is not certain; it may be restricted by hints which exclude
    certain colors or numbers from the card's possible identities.
    """
    def __init__(self, round_drawn, turn_drawn, rules):
        if rules:
            self.colors = {color for color in (Color)}
            if not rules['rainbow_enabled']: self.colors.discard(Color.MULTICOLOR)
        self.numbers = {*range(MIN_CARD_VALUE, MAX_CARD_VALUE + 1)}
        self.round_drawn = round_drawn
        self.color_guess = None
        self.number_guess = None
        self.round_updated, self.turn_updated = (round_drawn, turn_drawn)
        self.previous_states = []

    def hint_color_positive(self, color, rnd, trn, rules):
        """
        Update a card as a result of a color hint which mentions the card explicitly;
        for example, a hint which tells this card is blue.
        """
        if rules['rainbow_hint'] == 'wild':
            if color == color.MULTICOLOR:
                raise HanabiRulesException(f'Cannot hint {Color.MULTICOLOR} in wild-hint mode.')
            if not (color in self.colors or Color.MULTICOLOR in self.colors):
                raise HanabiSimException(
                    f'Inconsistent hints: color {style_text(color, color.name)}'\
                    f' is not possible for a hinted card.\nThe card:\n'\
                    f'{str(self)}'
                )
            if self.colors <= {color, Color.MULTICOLOR}: return self #nothing to do
            new_state = self.copy()
            #remove all colors which aren't the hinted color or rainbow
            new_state.colors = self.colors - (set(Color) - {color, Color.MULTICOLOR})
            new_state.previous_states.append(self)
            new_state.round_updated, new_state.turn_updated = (rnd, trn)
            return new_state
        #rules['rainbow_hint'] == 'suit'
        if (color not in self.colors):
            raise HanabiSimException(
                f'Inconsistent hints: color {style_text(color, color.name)}'\
                f' is not possible for a hinted card.\nThe card:\n'\
                f'{str(self)}'
            )
        if self.colors == {color}: return self #nothing to do
        new_state = self.copy()
        new_state.colors = {color}
        new_state.previous_states.append(self)
        new_state.round_updated, new_state.turn_updated = (rnd, trn)
        return new_state

    def hint_color_negative(self, color, rnd, trn, rules):
        """
        Update a card as a result of a color hint which mentions only other cards;
        for example, a hint which tells another card card is red.
        """
        if rules['rainbow_hint'] == 'wild':
            if color == color.MULTICOLOR:
                raise HanabiRulesException(f'Cannot hint {Color.MULTICOLOR} in wild-hint mode.')
            if not (color in self.colors or Color.MULTICOLOR in self.colors): return self #n.t.d.
            new_state = self.copy()
            new_state.colors = new_state.colors - {color, Color.MULTICOLOR}
            if len(new_state.colors) == 0:
                raise HanabiSimException(
                    f'Inconsistent hints: color {style_text(color, color.name)}'\
                    f' would disqualify all possible colors.\nThe card:\n'\
                    f'{str(self)}'
                )
            new_state.previous_states.append(self)
            new_state.round_updated, new_state.turn_updated = (rnd, trn)
            return new_state
        # rules['rainbow_hint'] == 'suit' 
        if (color not in self.colors): return self #nothing to do
        new_state = self.copy()
        new_state.colors.discard(color)
        if len(new_state.colors) == 0:
            raise HanabiSimException(
                f'Inconsistent hints; color {style_text(color, color.name)}'\
                f' would disqualify all possible colors for a non-hinted card.\n'\
                f'The card:\n{str(self)}'
            )
        new_state.previous_states.append(self)
        new_state.round_updated, new_state.turn_updated = (rnd, trn)
        return new_state

    def hint_number_positive(self, number, rnd, trn):
        """
        Update a card as a result of a number hint which mentions the card explicitly;
        for example, a hint which tells this card has value 3.
        """
        if (number not in self.numbers):
            raise HanabiSimException(
                f'Inconsistent hints; number {number} is not possible '\
                f'for a hinted card.\nThe card:\n{str(self)}'
            )
        if self.numbers == {number}: return self #nothing to do
        new_state = self.copy()
        new_state.numbers = {number}
        new_state.previous_states.append(self)
        new_state.round_updated, new_state.turn_updated = (rnd, trn)
        return new_state

    def hint_number_negative(self, number, rnd, trn):
        """
        Update a card as a result of a number hint which mentions only other cards;
        for example, a hint which tells another card has value 2.
        """
        if (number not in self.numbers): return self #nothing to do
        new_state = self.copy()
        new_state.numbers.discard(number)
        if len(new_state.numbers) == 0:
            raise HanabiSimException(
                f'Inconsistent hints; number {number} would disqualify all '\
                f'possible numbers for a non-hinted card.\nThe card:\n{str(self)}'
            )
        new_state.previous_states.append(self)
        new_state.round_updated, new_state.turn_updated = (rnd, trn)
        return new_state

    #TODO guess functionality may not be in line with the intended usage for hanabi-sim
    #consider reworking or deleting
    def guess_number(self, number):
        """
        Apply a player's guess of number to a card; example, the player guesses a card has value 1.
        """
        if (number not in self.numbers):
            raise HanabiSimException(
                f'Bad guess; number {number} was previously ruled out for guessed card.'
            )
        if number == self.number_guess: return self #nothing to do
        new_state = self.copy()
        new_state.number_guess = number
        new_state.previous_states.append(self)
        return new_state

    def guess_color(self, color):
        """
        Apply a player's guess of color to a card; example, the player guesses a card is green.
        """
        if (color not in self.colors):
            raise HanabiSimException(
                f'Bad guess; color {style_text(color, color.name)} '\
                f'was previously ruled out for guessed card.'
            )
        if color == self.color_guess: return self #nothing to do
        new_state = self.copy()
        new_state.color_guess = color
        new_state.previous_states.append(self)
        return new_state

    def __str__(self):
        #don't display colors which are impossible; display all colors which are possible;
        #use a special style for the guess, if any
        #Note we iterate on enum Color (not self.colors) to guarantee the same order
        colorstr = ''.join(
            [
                '' if color not in self.colors else
                guess_text(color, color.name[0]) if color == self.color_guess else
                style_text(color, color.name[0], deterministic=True)
                for color in Color
            ]
        )
        #display all possible numbers; display the guess (if any) in a special style
        #Note we iterate on the value range (not self.numbers, a set) to guarantee the order
        numberstr = ''.join(
            [
                guess_text(number, str(number)) if number == self.number_guess
                else str(number)
                for number in range(MIN_CARD_VALUE, MAX_CARD_VALUE + 1)
                if number in self.numbers
            ]
        )
        rep = tabulate(
            [
                [f'RD: {self.round_drawn}'],
                [colorstr],
                [f'RU: {self.round_updated}'],
                [f'TU: {self.turn_updated}'],
                [numberstr],
            ],
            tablefmt='pretty',
        )
        return rep

    def copy(self):
        cpy = UnknownCard(self.round_drawn, self.turn_updated, None)
        cpy.colors = self.colors.copy()
        cpy.numbers = self.numbers.copy()
        cpy.color_guess = self.color_guess
        cpy.number_guess = self.number_guess
        cpy.round_updated = self.round_updated 
        cpy.turn_updated = self.turn_updated
        cpy.previous_states = [c for c in self.previous_states]
        return cpy

    def num_possible_states(self):
        """
        A basic representation of the undertainty in a card, not accounting for
        any advanced information like discards which might rule out some states
        """
        return len(self.numbers) * len(self.colors)

    def __eq__(self, other):
        if not isinstance(other, UnknownCard): return False
        return self.colors == other.colors               and \
               self.numbers == other.numbers             and \
               self.color_guess == other.color_guess     and \
               self.number_guess == other.number_guess   and \
               self.round_drawn == other.round_drawn     and \
               self.round_updated == other.round_updated and \
               self.turn_updated == other.turn_updated   and \
               self.previous_states == other.previous_states


class RealizedCard:
    """
    A card of known value or number because it was played or discarded.
    """
    def __init__(self, identity, unrealized_state, was_rainbow = False):
        self.identity = identity #Card object
        self.unrealized_state = unrealized_state #UnknownCard object
        self.was_rainbow = was_rainbow #if this was a wild-play rainbow card

    def __eq__(self, other):
        if not isinstance(other, RealizedCard): return False
        return self.identity == other.identity and \
               self.unrealized_state == other.unrealized_state and \
               self.was_rainbow == other.was_rainbow

    def __str__(self):
        if self.was_rainbow:
            return str(Card(Color.MULTICOLOR, self.identity.number)) + '->' + str(self.identity)
        return str(self.identity)



