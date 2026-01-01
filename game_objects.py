from enum import Enum
from tabulate import tabulate
from colorama import Fore, Back, Style
from bisect import insort
from collections import defaultdict


class Color(Enum):
    BLUE = 1
    GREEN = 2
    RED = 3
    WHITE = 4
    YELLOW = 5

MIN_CARD_VALUE = 1
MAX_CARD_VALUE = 5
CARD_FREQUENCIES = [3,2,2,2,1]

PRINT_STYLE = {
    Color.BLUE:   Fore.LIGHTBLUE_EX,
    Color.RED:    Fore.LIGHTRED_EX,
    Color.YELLOW: Fore.LIGHTYELLOW_EX,
    Color.WHITE:  Fore.LIGHTWHITE_EX,
    Color.GREEN:  Fore.GREEN
}

SUSPICION_STYLE = defaultdict(lambda: f'{Back.LIGHTWHITE_EX}{Fore.BLACK}') | {
    Color.BLUE:   Back.BLUE, 
    Color.RED:    Back.RED,
    Color.YELLOW: f'{Back.LIGHTYELLOW_EX}{Fore.BLACK}',
    Color.WHITE:  f'{Back.LIGHTWHITE_EX}{Fore.BLACK}',
    Color.GREEN:  Back.GREEN
}

def style_text(color, text):
    """
    color: a Color object or a valid colorama color
    text: arbitrary text to be colored
    """
    if isinstance(color, Color):
        return f'{PRINT_STYLE[color]}{text}{Style.RESET_ALL}'
    else:
        return f'{color}{text}{Style.RESET_ALL}'

def guess_text(color, text):
    """
    color: a Color object or a valid colorama color
    text: arbitrary text to be colored
    """
    return f'{SUSPICION_STYLE[color]}{text}{Style.RESET_ALL}'


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
        if not isinstance(other, Card):
            return False
        return self.color == other.color and self.number == other.number

    def copy(self):
        return self


class PlayedCards:
    """
    A collection of cards which have been played successfully, adding to a firework.
    """
    def __init__(self):
        self.cards = {color : Card(color, 0) for color in (Color)}

    def add(self, card):
        color = card.color
        if not (self.cards[color].number + 1 == card.number): raise HanabiSimException('')#TODO be more elegant here
        new_state = self.copy()
        new_state.cards[color] = card
        return new_state

    def values(self):
        return self.cards.values()

    def copy(self):
        cpy = PlayedCards()
        cpy.cards = {k : v for k, v in self.cards.items()} #color and Cards immutable
        return cpy

    def __str__(self):
        return tabulate([[style_text(color, self.cards[color]) for color in self.cards]],
                        tablefmt = 'pretty')

    def __getitem__(self, key):
        return self.cards[key]
 

class OutstandingCards:
    """
    A collection of all cards in the game of Hanabi using rules which do not
    include rainbows.  Updated throughout the game to exclude cards revealed
    by discards and plays.  Notably, cards which are in players' hands are
    considered to be outstanding because they are not publicly known.
    """
    def __init__(self):
        self.cards = []

        for color in (Color):
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
        data = [[style_text(color, color.name) for color in Color]]
        #Sort outstanding cards by color
        columns = [ [*filter(lambda card: card.color == color, self.cards)] for color in Color ]
        table_length = max([len(col) for col in columns])
        #Create table rows.  Each row is the next card number of that color, or empty if no
        #cards of that color remain.
        for i in range(table_length):
            row = [columns[j][i] if len(columns[j]) >= i + 1 else ' ' for j in range(len(Color))]
            data.append(row)
        return tabulate(data, headers='firstrow', tablefmt = 'pretty')
    
    def copy(self):
        cpy = OutstandingCards()
        #cards immutable; no deep copy needed
        cpy.cards = self.cards.copy()
        return cpy


class DiscardedCards:
    """
    A collection of all cards which have been discarded.
    """
    def __init__(self):
        self.cards = {color : [] for color in (Color)}

    def add(self, card):
        new_state = self.copy()
        insort(new_state.cards[card.color], card, key = lambda c: c.number)
        return new_state

    def copy(self):
        cpy = DiscardedCards()
        cpy.cards = {color : lst.copy() for color, lst in self.cards.items()} #shallow copy lists
        return cpy

    def __str__(self):
        #Have as many rows as needed to fit all the cards of the most-discarded color
        table_length = max([len(l) for l in self.cards.values()])

        header = [style_text(color, color.name) for color in Color]
        data = [header]
        for i in range(table_length):
            #Create table rows.  Each row is the next card number of that color, or empty if no
            #cards of that color remain.
            row = [self.cards[color][i] if len(self.cards[color]) >= i + 1 else ' ' for color in Color]
            data.append(row)
        return tabulate(data, headers='firstrow', tablefmt = 'pretty')


class GameState:
    """
    A representation of the current public information available in a game of Hanabi
    """
    STARTING_MISFIRES, MAX_MISFIRES = 0, 2 #2 misfires => OK; 3 misfires => lose
    STARTING_HINTS, MAX_HINTS = 8, 8
    STARTING_DISCARD = {color : [] for color in (Color)}
    STARTING_PLAYER_UP = 0
    STARTING_ROUND = 1
    MIN_PLAYERS, MAX_PLAYERS = 2, 5
    HAND_SIZES = {2:5, 3:5, 4:4, 5:4}
    
    default_players = ['Player0', 'Player1', 'Player2']
    default_protocols = ['in_place', 'left_shift', 'right_shift']

    def __init__(self, players=default_players, protocols=default_protocols):
        self.misfires = self.STARTING_MISFIRES
        self.hints = self.STARTING_HINTS
        self.play = PlayedCards()
        self.discard = DiscardedCards()
        self.player_up = self.STARTING_PLAYER_UP
        self.round = self.STARTING_ROUND
        self.num_players = len(players)
        if not (self.MIN_PLAYERS <= self.num_players <= self.MAX_PLAYERS):
            raise HanabiRulesException(f'Invalid number ({self.num_players}) of players; '\
                                       f'{self.MIN_PLAYERS} to {self.MAX_PLAYERS} allowed.')
        if (len(protocols) != self.num_players):
            raise HanabiSimException(f'There must be exactly one protocol per player (players: '\
                                     f'{self.num_players}; protocols: {len(protocols)})')
        self.players = [Player(name, self.HAND_SIZES[self.num_players], self, protocol) \
                        for name, protocol in zip(players, protocols)]
        self.outstanding_cards = OutstandingCards()
        self.num_in_deck = len(self.outstanding_cards) - sum([len(p.hand) for p in self.players])
        self.over = False
        self.previous_state = None
        self.turns_taken = []

    def represent_play(self):
        return str(self.play)

    def represent_discard(self):
        return str(self.discard)

    def represent_general(self):
        players = 'Players (in order): ' + ', '.join([p.name for p in self.players]) + '\n'
        return players + tabulate([
                   ['Round', 'Player Up', 'Hints', 'Misfires'],
                   [self.round, self.players[self.player_up].name, self.hints, self.misfires]
               ],
               headers='firstrow',
               tablefmt='pretty'
        )

    def copy(self):
        players_copy = [p.copy() for p in self.players]
        cpy = GameState([None] * self.num_players, [None] * self.num_players)
        for p in players_copy:
            p.game = cpy
        cpy.misfires = self.misfires
        cpy.hints = self.hints
        cpy.play = self.play
        cpy.discard = self.discard
        cpy.player_up = self.player_up
        cpy.round = self.round
        cpy.num_players = self.num_players
        cpy.players = players_copy
        cpy.outstanding_cards = self.outstanding_cards # OutstandingCards immutable
        cpy.num_in_deck = self.num_in_deck
        cpy.over = self.over
        cpy.previous_state = self.previous_state
        cpy.turns_taken = self.turns_taken.copy()
        return cpy

    def __str__(self):
        play = self.represent_play()
        discard = self.represent_discard()
        other_state = self.represent_general() 
        return f'General:\n{other_state}\nplay:\n{play}\ndiscard:\n{discard}\n'

    #get a player specified by a number in turn order or an unambiguous string
    #of characters which begins the player's name
    def get_player(self, specifier):
        if isinstance(specifier, int):
            try: return self.players[specifier]
            except IndexError as e:
                raise IndexError(f'There is no {specifier} player; number of '\
                                 f'players: {self.num_players}')
        elif isinstance(specifier, str):
            s = set()
            for p in self.players:
                if p.name.lower().startswith(specifier.lower()):
                    s.add(p)
            if (len(s) == 1): return s.pop()
            else:
                raise KeyError(f"Specifier {specifier} failed to uniquely identify a player; "\
                               f"found [{',  '.join([p.name for p in s])}] (\"show state\" for players)")
        raise KeyError(f'Specified player {specifier} not found among player list.')
 
    def advance_turn(self):
        self.player_up += 1
        self.round += self.player_up // self.num_players
        self.player_up = self.player_up % self.num_players

class UnknownCard:
    """
    A card whose identity is not certain; it may be restricted by hints which exclude
    certain colors or numbers from the card's possible identities.
    """
    def __init__(self, round_drawn, turn_drawn):
        self.colors = {color for color in (Color)}
        self.numbers = {*range(MIN_CARD_VALUE, MAX_CARD_VALUE + 1)}
        self.round_drawn = round_drawn
        self.color_guess = None
        self.number_guess = None
        self.round_updated, self.turn_updated = (round_drawn, turn_drawn)
        self.previous_states = []

    def hint_color_positive(self, color, rnd, trn):
        """
        Update a card as a result of a color hint which mentions the card explicitly;
        for example, a hint which tells this card is blue.
        In this example, the proper response is to remove all possible colors except blue.
        """
        if (color not in self.colors):
            raise HanabiSimException(f'Inconsistent hints: color {style_text(color, color.name)}'\
                                     f' was previously ruled out for a hinted card.\nThe card:\n'\
                                     f'{str(self)}')
        if self.colors == {color}: return self #nothing to do
        new_state = self.copy()
        new_state.colors = {color}
        new_state.previous_states.append(self)
        new_state.round_updated, new_state.turn_updated = (rnd, trn)
        return new_state

    def hint_color_negative(self, color, rnd, trn):
        """
        Update a card as a result of a color hint which mentions only other cards;
        for example, a hint which tells another card card is red.
        In this case, the proper response is to update the card to disallow being red.
        """
        if (color not in self.colors): return self #nothing to do
        new_state = self.copy()
        new_state.colors.discard(color)
        if len(new_state.colors) == 0:
            raise HanabiSimException(f'Inconsistent hints; color {style_text(color, color.name)}'\
                                     f' was the only possible color for a non-hinted card.\n'\
                                     f'The card:\n{str(self)}') 
        new_state.previous_states.append(self)
        new_state.round_updated, new_state.turn_updated = (rnd, trn)
        return new_state

    def hint_number_positive(self, number, rnd, trn):
        """
        Update a card as a result of a number hint which mentions the card explicitly;
        for example, a hint which tells this card has value 3.
        In this example, the proper response is to update the card to remove all possible values except 3.
        """
        if (number not in self.numbers):
            raise HanabiSimException(f'Inconsistent hints; number {number} was '\
                                     f'previously ruled out for a hinted card.\n'\
                                     f'The card:\n{str(self)}')
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
        In this example, the proper response is to update the card to disallow having value 3.
        """
        if (number not in self.numbers): return self #nothing to do
        new_state = self.copy()
        new_state.numbers.discard(number)
        if len(new_state.numbers) == 0:
            raise HanabiSimException(f'Inconsistent hints; number {number} was the '\
                                     f'only possible number for a non-hinted card.\n'\
                                     f'The card:\n{str(self)}')
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
            raise HanabiSimException(f'Bad guess; number {number} was previously '\
                                     f'ruled out for guessed card.')
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
            raise HanabiSimException(f'Bad guess; color {style_text(color, color.name)} '\
                                     f'was previously ruled out for guessed card.')
        if color == self.color_guess: return self #nothing to do
        new_state = self.copy()
        new_state.color_guess = color
        new_state.previous_states.append(self)
        return new_state

    def __str__(self):
        #don't display colors which are impossible; display all colors which are possible;
        #use a special style for the guess, if any
        #Note we iterate on enum Color (not self.colors) to guarantee the same order
        colorstr = ''.join([
            '' if color not in self.colors else
            guess_text(color, color.name[0]) if color == self.color_guess else
            style_text(color, color.name[0]) for color in Color
        ])
        #display all possible numbers; display the guess (if any) in a special style
        #Note we iterate on self.numbers which gives us the same order always
        #TODO self.numbers is a set; is the consistent ordering just a coincidence or guaranteed?
        numberstr = ''.join([
            guess_text(number, str(number)) if number == self.number_guess
            else str(number) for number in self.numbers
        ])
        rep = tabulate([[f'RD: {self.round_drawn}'],
                        [colorstr],
                        [f'RU: {self.round_updated}'],
                        [f'TU: {self.turn_updated}'],
                        [numberstr]], \
                        tablefmt='pretty')
        return rep

    def show_past_states(self):
        fake_hand = Hand(0) #a bit of a hack, but we basically want the same representation
        fake_hand.hand = [*self.previous_states, self]
        return str(fake_hand)

    def copy(self):
        cpy = UnknownCard(self.round_drawn, self.turn_updated)
        cpy.colors = self.colors.copy()
        cpy.numbers = self.numbers.copy()
        cpy.color_guess = self.color_guess
        cpy.number_guess = self.number_guess
        cpy.round_updated = self.round_updated 
        cpy.turn_updated = self.turn_updated
        cpy.previous_states = [c for c in self.previous_states]
        return cpy

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
    def __init__(self, identity, unrealized_state):
        self.identity = identity #Card object
        self.unrealized_state = unrealized_state #UnknownCard object

    def __eq__(self, other):
        if not isinstance(other, RealizedCard): return False
        return self.identity == other.identity and \
               self.unrealized_state == other.unrealized_state

class Hand:
    """
    A collection of the cards in the hand of a player
    """
    def __init__(self, HAND_SIZE):
        self.hand = [UnknownCard(0, '-') for _ in range(HAND_SIZE)]

    def process_hint(self, positions, hint, r, t):
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
                try: 
                    new_hand.hand[i] = card.hint_color_positive(hint, r, t) if i in positions \
                                       else card.hint_color_negative(hint, r, t)
                except HanabiSimException as e:
                    raise HanabiIndexException(i, *e.args)
            else:
                try:
                    new_hand.hand[i] = card.hint_number_positive(hint, r, t) if i in positions \
                                  else card.hint_number_negative(hint, r, t)
                except HanabiSimException as e:
                    raise HanabiIndexException(i, *e.args)
        return new_hand

    def process_guess(self, position, guess):
        try: card = self.hand[position]
        except IndexError: raise HanabiIndexException(position)
        if isinstance(guess, int):
            if guess not in card.numbers:
                raise HanabiSimException('Bad guess; number already disqualified')
            new_card_state = card.guess_number(guess)
        elif isinstance(guess, Color):
            if guess not in card.colors:
                raise HanabiSimException('Bad guess; color already disqualified')
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

    def replace_card(self, cur_round, position, player):
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
                new_hand.hand.append(UnknownCard(cur_round, player.name))
            case 'right_shift':
                #The new card is 1; if n is played then 1 becomes 2, ... n - 1 becomes n
                del new_hand.hand[position]
                new_hand.hand.insert(0, UnknownCard(cur_round, player.name))
            case 'in_place':
                #The new card takes the place of the old card.  If 3 is played, the new card is 3
                new_hand.hand[position] = UnknownCard(cur_round, player.name)
            case _:
                raise HanabiSimException('Illegal replenishment protocol')
        return new_hand

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
                style_text(color, color.name[0]) for color in Color
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
        cpy = Hand(len(self.hand))
        cpy.hand = [card for card in self.hand] #UnknownCard immutable; shallow copy safe 
        return cpy


class Player:
    """
    A player in the game of Hanabi, who holds a hand and performs actions to advance the game.
    """
    def __init__(self, name, hand_size, game, replenishment_protocol='in_place'):
        self.name = name
        self.hand = Hand(hand_size)
        self.replenishment_protocol = replenishment_protocol
        self.game = game

    def perform_discard(self, position, card, verbose=False):
        """
        Attempt to perform a discard, updating state of the discarded cards, hints,
        and hand of the player performing the discard.
        """
        if (self.game.hints == self.game.MAX_HINTS):
            raise HanabiRulesException('Cannot discard while hints are at maximum!')
        if (not 0 <= position < len(self.hand)):
            errstr = 'the position given was not in range.\n'\
                     f'Expected an integer between 1 and {len(self.hand)}, inclusive.'
            raise HanabiIndexException(position, errstr)
        if card.color  not in self.hand[position].colors or\
           card.number not in self.hand[position].numbers:
            errstr = f'The card identity {card} which you gave was not possible '\
                     f'given prior hints.\nThe card:\n{str(self.hand[position])}'
            raise HanabiIndexException(position, errstr)
        new_state = self.game.copy()
        new_state.hints += 1
        #Put the card in the discard pile for its color; keep the pile sorted numerically
        new_state.discard = new_state.discard.add(card)
        new_state.turns_taken.append(('discard', RealizedCard(card, self.hand[position])))
        try: new_state.outstanding_cards = new_state.outstanding_cards.remove(card)
        except ValueError:
            errstr = f'The card you specified, {card}, is exhausted '\
                     f'by prior plays and discards. (see "show outstanding")'
            raise HanabiSimException(errstr)
        #Replenishment
        player = new_state.get_player(self.game.player_up)
        if (new_state.num_in_deck > 0):
            player = new_state.get_player(self.game.player_up)
            new_state.num_in_deck -= 1
            player.hand = player.hand.replace_card(new_state.round, position, player)
        else:
            player.hand = player.hand.copy()
            del player.hand.hand[position]
        new_state.previous_state = self.game
        new_state.advance_turn()
        if verbose: print(str(player))
        return new_state

    def perform_play(self, position, card, verbose=False):
        """
        Attempt to perform a play, updating the played cards or discarded cards (as applicable)
        and the hand of the player performing the discard.
        """
        if (not 0 <= position < len(self.hand)):
            errstr = 'the position you specified was not in range.\n'\
                     f'Expected an integer between 1 and {len(self.hand)}, inclusive.'
            raise HanabiIndexException(position, errstr)
        if card.color not in self.hand[position].colors or \
           card.number not in self.hand[position].numbers:
            errstr = f'The card identity {card} which you gave was not possible '\
                     f'given prior hints.\nThe card:\n{str(self.hand[position])}'
            raise HanabiIndexException(position, errstr)
        new_state = self.game.copy()
        #successful play
        if (card.number == new_state.play[card.color].number + 1):
            new_state.turns_taken.append(('play', RealizedCard(card, self.hand[position])))
            new_state.play = new_state.play.add(card)
            if card.number == MAX_CARD_VALUE:
                new_state.hints += 1 if new_state.hints < new_state.MAX_HINTS else 0
                if all([c.number == MAX_CARD_VALUE for c in new_state.play.values()]):
                    new_state.over = True
        #unsuccessful play
        else:
            new_state.turns_taken.append(('misfire', RealizedCard(card, self.hand[position])))
            new_state.misfires += 1
            new_state.over = new_state.misfires > new_state.MAX_MISFIRES
            new_state.hints += 1 if new_state.hints < new_state.MAX_HINTS else 0
            new_state.discard = new_state.discard.add(card)
        #update outstanding and replenish in any event
        try: new_state.outstanding_cards = new_state.outstanding_cards.remove(card)
        except ValueError:
            errstr = f'The card you specified, {card}, is exhausted '\
                     f'by prior plays and discards. (see "show outstanding")' 
            raise HanabiSimException(errstr)
        player = new_state.get_player(self.game.players.index(self)) #get player in new state
        if (new_state.num_in_deck > 0):
            new_state.num_in_deck -= 1
            player.hand = player.hand.replace_card(new_state.round, position, player)
        else:
            player.hand = player.hand.copy()
            del player.hand.hand[position]
        new_state.previous_state = self.game
        new_state.advance_turn()
        if verbose: print(str(player))
        return new_state

    def perform_hint(self, target_player, positions, hint, verbose=False):
        """
        Attempt to perform a hint, updating the game state and the hand of the hinted player.
        """
        if self.game.hints <= 0:
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

        new_state = self.game.copy()
        new_state.hints -= 1
        new_state.previous_state = self.game
        new_state.turns_taken.append(('hint', target_player.name, isinstance(hint, int), positions))
        player = new_state.get_player(self.game.players.index(target_player))
        try: 
            player.hand = player.hand.process_hint(positions, hint, new_state.round, self.name)
        except HanabiIndexException as e:
            raise e
        new_state.advance_turn()
        if verbose: print(str(player))
        return new_state

    #TODO guess functionality may not be in line with the intended use of hanabi-sim
    #decide whether it should be disabled
    def perform_guess(self, position, guess, verbose=False):
        """
        Apply the player's guess of color or number to a card.
        This does not consume a player's turn; it just updates the card with the guess.
        """
        if not isinstance(position, int) or not (0 <= position < len(self.hand)):
            raise HanabiIndexException(position, f'Invalid position ({position}) given.')
        new_state = self.game.copy()
        player = new_state.get_player(self.game.players.index(self)) #get player in new state
        try: player.hand = player.hand.process_guess(position, guess)
        except (HanabiSimException, HanabiIndexException) as e: raise e
        new_state.previous_state = self.game
        if verbose: print(str(player))
        return new_state

    def perform_swap(self, pos1, pos2, verbose=False):
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

        new_state = self.game.copy()
        player = new_state.get_player(self.game.players.index(self)) #get player in new state
        try: player.hand = player.hand.process_swap(pos1, pos2)
        except HanabiIndexException as e: raise e
        new_state.previous_state = self.game
        if verbose: print(str(player))
        return new_state

    def copy(self):
        cpy = Player(self.name, 0, self.game, self.replenishment_protocol)
        cpy.hand = self.hand.copy()
        cpy.game = self.game
        return cpy

    def __str__(self):
        return str(f'{self.name}:\n{self.hand}')

    def represent_card(self, position):
        """
        Show a card in all the states it has held over time, up to and including now.
        """
        return self.hand[position].show_past_states()
        
         
 
class HanabiRulesException(Exception):
    """
    Used when an action would break a rule of Hanabi.
    Example: hinting oneself.
    """
    def __init__(self, *args):
        super().__init__(*args)

    def __str__(self):
        return f'{self.message}'

class HanabiSimException(Exception):
    """
    Used when an action doesn't make sense in the context of
    the current simulation.
    Example: Discarding the red 5 when it is already played
    """
    def __init__(self, *args):
        super().__init__(*args)

    def __str__(self):
        return f'{self.message}'

#Useful when a problem occurs 
class HanabiIndexException(Exception):
    """
    Used when an action doesn't make sense, and the action takes
    place at a particular index in a hand which it is useful to
    propagate upwards to functions which can print errors based on it.
    Because indexing is different in the objects (0-based) and the
    user interface (1-based), game objects should just raise these errors
    with the index they understand and let the higher functions decide
    how to handle them (usually by adding 1).
    """
    def __init__(self, index, *args):
        super().__init__(*args)
        self.index = index
