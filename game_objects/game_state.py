from tabulate import tabulate
from collections import defaultdict

from game_objects.rules import HanabiRuleset
from game_objects.color import Color
from game_objects.card import Card
from game_objects.card import MAX_CARD_VALUE
from game_objects.card_collections import PlayedCards, OutstandingCards, DiscardedCards
from game_objects.player import Player
from game_objects.actions import HintAction, DiscardAction, PlayAction, MisfireAction
from game_objects.actions import ActionMetadata
from game_objects.exceptions import (
    HanabiRulesException, HanabiSimException, HanabiInputException,
)


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
    default_rules = HanabiRuleset()
    game_end_index = None #the index of the player who draws the last card, when applicable

    def __init__(self, players=default_players, protocols=default_protocols, ruleset=default_rules):
        self.rules = ruleset
        self.misfires = self.STARTING_MISFIRES
        self.hints = self.STARTING_HINTS + self.rules['extra_hints']
        self.player_up = self.STARTING_PLAYER_UP
        self.round = self.STARTING_ROUND
        self.num_players = len(players)
        if not (self.MIN_PLAYERS <= self.num_players <= self.MAX_PLAYERS):
            raise HanabiRulesException(f'Invalid number ({self.num_players}) of players; '\
                                       f'{self.MIN_PLAYERS} to {self.MAX_PLAYERS} allowed.')
        if (len(protocols) != self.num_players):
            raise HanabiSimException(f'There must be exactly one protocol per player (players: '\
                                     f'{self.num_players}; protocols: {len(protocols)})')
        self.players = [Player(name, \
                               self.HAND_SIZES[self.num_players] + \
                               self.rules['extra_cards'], self.rules, \
                               protocol \
                        ) \
                        for name, protocol in zip(players, protocols)]
        self.outstanding_cards = OutstandingCards(self.rules)
        self.play = PlayedCards(self.rules)
        self.discard = DiscardedCards(self.rules)
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
        fields = ['Round', 'Player Up', 'Hints', 'Misfires', 'Deck Size']
        values = [self.round, self.players[self.player_up].name, self.hints, self.misfires,
                  self.num_in_deck]
        if self.rules['game_end'] == 'final_round' and self.game_end_index is not None:
            fields.append('Final Player')
            values.append(self.get_player(self.game_end_index).name)
        table =  tabulate([fields, values], headers='firstrow', tablefmt='pretty')
        return players + table

    def get_turn_metadata(self):
        """
        Return one ActionMetadata per turn, pairing each action with the round
        and acting player derived from its position in turns_taken.
        """
        return [
            ActionMetadata(action, 1 + i // self.num_players, i % self.num_players)
            for i, action in enumerate(self.turns_taken)
        ]

    def get_actions_of_player(self, player_index):
        """
        Return the metadata of every action taken by the given player.
        """
        if not 0 <= player_index < self.num_players:
            raise IndexError('Unreasonable player specified.')
        return [md for md in self.get_turn_metadata() if md.player == player_index]

    def get_actions_of_type(self, typ):
        """
        Return the metadata of every action of the given type.
        """
        if typ not in {PlayAction, DiscardAction, MisfireAction, HintAction}:
            raise RuntimeError('Unreasonable action type queried.')
        return [md for md in self.get_turn_metadata() if isinstance(md.action, typ)]

    def copy(self):
        cpy = GameState()
        cpy.rules = self.rules
        cpy.misfires = self.misfires
        cpy.hints = self.hints
        cpy.play = self.play
        cpy.discard = self.discard
        cpy.player_up = self.player_up
        cpy.round = self.round
        cpy.num_players = self.num_players
        cpy.players = [p for p in self.players]
        cpy.outstanding_cards = self.outstanding_cards # OutstandingCards immutable
        cpy.num_in_deck = self.num_in_deck
        cpy.game_end_index = self.game_end_index
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
    #TODO make this function return both index and player or add a method to get the index
    def get_player(self, specifier):
        if isinstance(specifier, int):
            if not 0 <= specifier < self.num_players:
                raise HanabiInputException(
                    f'There is no player {specifier + 1}; number of players: {self.num_players}'
                )
            return self.players[specifier]
        elif isinstance(specifier, str):
            s = set()
            for p in self.players:
                if p.name.lower().startswith(specifier.lower()): s.add(p)
            if (len(s) == 1): return s.pop()
            else:
                #sort by turn order so the message is deterministic
                found = ', '.join([p.name for p in sorted(s, key=self.players.index)])
                raise HanabiInputException(
                    f"Specifier {specifier} failed to uniquely identify a player; "
                    f"found [{found}] (\"show state\" for players)")
        raise HanabiInputException(f'Specified player {specifier} not found among player list.')

    #returns True if there exists a way to successfully play the 5 card for every suit
    #and False otherwise
    def is_satisfiable(self):
        
        demanded_rainbow_cards = defaultdict(lambda: 0)
        #for every Card(color, number) not yet played, check if we have one available
        for color, card in self.play.cards.items():
            for val in range(card.number + 1, MAX_CARD_VALUE + 1):
                if not self.outstanding_cards.contains(Card(color, val)):
                    #if we lack the card and rainbows aren't wild, it's unsatisfiable
                    if self.rules['rainbow_play'] != 'wild': return False
                    #if rainbows are wild, we need a rainbow of the same number
                    else: demanded_rainbow_cards[val] += 1

        #check if we have enough rainbows to cover if rainbows wild; dict is empty if not wild
        for val, count in demanded_rainbow_cards.items():
            if not self.outstanding_cards.contains(Card(Color.MULTICOLOR, val), count): return False
        return True
                
 
    def advance_turn(self):
        if self.rules['game_end'] == 'until_done' and not self.is_satisfiable():
            print('An essential card was discarded; the game is lost.')
            self.over = True
        if self.rules['game_end'] == 'final_round':
            if self.player_up == self.game_end_index:
                print('The player who drew the last card has gone again; the game is over.')
                self.over = True
            elif self.game_end_index is None and self.num_in_deck == 0:
                print('The last card has been drawn; one round remains.')
                self.game_end_index = self.player_up
        self.player_up += 1
        self.round += self.player_up // self.num_players
        self.player_up = self.player_up % self.num_players

