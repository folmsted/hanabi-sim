from collections import namedtuple
from color import Color

HanabiRule = namedtuple('HanabiRule', ['value', 'short_form', 'allowed_values', 'description'])

class HanabiRuleset:

    RAINBOW_ENABLED_OPTIONS =  {True, False}
    RAINBOW_HINT_OPTIONS =     {'wild', 'suit'}
    RAINBOW_PLAY_OPTIONS =     {'wild', 'suit'}
    BOMBS_GIVE_HINTS_OPTIONS = {True, False}
    EXTRA_CARDS_OPTIONS =      range(-1, 2)
    EXTRA_HINTS_OPTIONS =      range(-8, 4)
    GAME_END_OPTIONS =         {'until_done','final_round'}

    DEFAULT_RAINBOW_ENABLED =  False
    DEFAULT_RAINBOW_HINT =     'suit'
    DEFAULT_RAINBOW_PLAY =     'suit'
    DEFAULT_BOMBS_GIVE_HINTS = True #contrary to actual rules, but this is more fun
    DEFAULT_EXTRA_CARDS =      0
    DEFAULT_EXTRA_HINTS =      0
    DEFAULT_GAME_END =         'until_done'

    #short forms for handling user-input commmands.  MUST NOT REPEAT
    RAINBOW_ENABLED_SHORT_FORM =  're'
    RAINBOW_HINT_SHORT_FORM =     'rh'
    RAINBOW_PLAY_SHORT_FORM =     'rp'
    BOMBS_GIVE_HINTS_SHORT_FORM = 'bgh'
    EXTRA_CARDS_SHORT_FORM =      'ec'
    EXTRA_HINTS_SHORT_FORM =      'eh'
    GAME_END_SHORT_FORM =         'ge'

    RAINBOW_ENABLED_DESC = \
        f'Determines whether the game will be played with rainbow ({Color.MULTICOLOR}) cards.\n'\
        f'If True, rainbow cards will be used.  If False, they will not.\n'\
        f'When True, enables the rules for handling rainbow cards.'
    RAINBOW_HINT_DESC = \
        f'Determines whether rainbow ({Color.MULTICOLOR}) cards are wild when hinted.\n'\
        f'If "wild", rainbow cards will always be treated as matching\n'\
        f'the color of a hint, and the rainbow color cannot be hinted.\n'\
        f'If "suit", rainbow can be hinted and only matches hints of\n'\
        f'rainbow color.  Rule available only if rainbow_enabled is True.'
    RAINBOW_PLAY_DESC = \
        f'Determines whether rainbow ({Color.MULTICOLOR}) cards play into a separate suit\n'\
        f'(when set to "suit") or whether they are wild when played\n'\
        f'(when set to "wild").  A "wild" rainbow card can add to any\n'\
        f'color\'s firework for which its number is valid when played,\n'\
        f'determined by the player playing the card.  A "suit" rainbow\n'\
        f'card plays into the rainbow suit.'
    BOMBS_GIVE_HINTS_DESC = \
        'Determines whether wrongly played cards (triggering a misfire)\n'\
        'give a hint.  If True, a misfired card will restore a hint if\n'\
        'hints are below maximum.  If False, this will not happen.'
    EXTRA_CARDS_DESC = \
        'Modifies the number of cards each player is dealt and holds.\n'\
        'Negative numbers reduce hand size.'
    EXTRA_HINTS_DESC = \
        f'Modifies the number of hints the players start with.\n'\
        f'Negative numbers reduce the number of hints.  Notably,\n'\
        f'the maximum number of hints (8) is not affected.\n'\
        f'Starting hints in excess of maximum are not lost until used\n'\
        f'but cannot be replenished, since discarding is illegal if\n'\
        f'the number of hints would be brought above maximum.'
    GAME_END_DESC = \
        f'Determines the nature of the end of the game.  If set to \n'\
        f'"until_done", the game continues until the players exhaust all misfires,\n'\
        f'discard an essential card, or complete all fireworks.  If set to \n'\
        f'"final_round", after the last card is drawn, one complete \n'\
        f'round is taken, ending with the player who drew the last card,\n'\
        f'at which point the game is over.'

    def __init__(self, rainbow_enabled  = DEFAULT_RAINBOW_ENABLED,
                       rainbow_hint     = DEFAULT_RAINBOW_HINT,
                       rainbow_play     = DEFAULT_RAINBOW_PLAY,
                       bombs_give_hints = DEFAULT_BOMBS_GIVE_HINTS,
                       extra_cards      = DEFAULT_EXTRA_CARDS,
                       extra_hints      = DEFAULT_EXTRA_HINTS,
                       game_end         = DEFAULT_GAME_END):

        self.rainbow_enabled = HanabiRule(rainbow_enabled, self.RAINBOW_ENABLED_SHORT_FORM, \
                                       self.RAINBOW_ENABLED_OPTIONS, self.RAINBOW_ENABLED_DESC)
        if self.rainbow_enabled.value not in self.rainbow_enabled.allowed_values:
            raise ValueError(f'rainbow_enabled must be one of {self.RAINBOW_ENABLED_OPTIONS}.')

        self.rainbow_hint = HanabiRule(rainbow_hint, self.RAINBOW_HINT_SHORT_FORM, \
                                       self.RAINBOW_HINT_OPTIONS, self.RAINBOW_HINT_DESC)
        if self.rainbow_hint.value not in self.rainbow_hint.allowed_values:
            raise ValueError(f'rainbow_hint must be one of {self.RAINBOW_HINT_OPTIONS}.')

        self.rainbow_play = HanabiRule(rainbow_play, self.RAINBOW_PLAY_SHORT_FORM, \
                                       self.RAINBOW_PLAY_OPTIONS, self.RAINBOW_PLAY_DESC)
        if self.rainbow_play.value not in self.rainbow_play.allowed_values:
            raise ValueError(f'rainbow_play must be one of {self.RAINBOW_PLAY_OPTIONS}.')

        self.bombs_give_hints = HanabiRule(bombs_give_hints, self.BOMBS_GIVE_HINTS_SHORT_FORM, \
                                     self.BOMBS_GIVE_HINTS_OPTIONS, self.BOMBS_GIVE_HINTS_DESC)
        if self.bombs_give_hints.value not in self.bombs_give_hints.allowed_values:
            raise ValueError(f'bombs_give_hints must be one of {self.BOMBS_GIVE_HINTS_OPTIONS}.')

        self.extra_cards = HanabiRule(extra_cards, self.EXTRA_CARDS_SHORT_FORM, \
                                      self.EXTRA_CARDS_OPTIONS, self.EXTRA_CARDS_DESC)
        if self.extra_cards.value not in self.extra_cards.allowed_values:
            raise ValueError(f'extra_cards must be one of {self.EXTRA_CARDS_OPTIONS}.')

        self.extra_hints = HanabiRule(extra_hints, self.EXTRA_HINTS_SHORT_FORM, \
                                      self.EXTRA_HINTS_OPTIONS, self.EXTRA_HINTS_DESC)
        if self.extra_hints.value not in self.extra_hints.allowed_values:
            raise ValueError(f'extra_hints must be one of {self.EXTRA_HINTS_OPTIONS}.')

        self.game_end = HanabiRule(game_end, self.GAME_END_SHORT_FORM, \
                                   self.GAME_END_OPTIONS, self.GAME_END_DESC)
        if self.game_end.value not in self.game_end.allowed_values:
            raise ValueError(f'game_end must be one of {self.GAME_END_OPTIONS}.')

    def change_rule(self, rule, value):
        """
        Change a user-chosen rule to the user-chosen value, or fail if the (rule, value)
        pair is not appropriate.  rule and value are user-input strings which must be
        converted to the appropriate format.
        """
        try: k, v = self._get_rule(rule)
        except KeyError as e: raise HanabiSimException(f'No such rule: "{rule}".')
        match k:
            case 'rainbow_enabled' | 'bombs_give_hints':
                new_value = not v.value if value is None else \
                            True if 'true'.startswith(value.lower()) else \
                            False if 'false'.startswith(value.lower()) else value
            case 'rainbow_hint' | 'rainbow_play' if self['rainbow_enabled']:
                new_value = (v.allowed_values - {v.value}).pop() if value is None else \
                            'suit' if 'suit'.startswith(value.lower()) else \
                            'wild' if 'wild'.startswith(value.lower()) else value
            case 'rainbow_hint' | 'rainbow_play' if not self['rainbow_enabled']:
                raise HanabiRulesException('No rainbows in this game to toggle the handling of.')
            case 'game_end':
                new_value = (v.allowed_values - {v.value}).pop() if value is None else \
                            'final_round' if 'final_round'.startswith(value.lower()) else \
                            'until_done' if 'until_done'.startswith(value.lower()) else value
            case 'extra_cards' | 'extra_hints':
                try: new_value = int(value)
                except ValueError as e:
                    raise HanabiSimException(f'Invalid option {value} for rule {k}')
                except TypeError as e:
                    raise HanabiSimException(f'You must input a value to give the rule.')

        if new_value not in v.allowed_values:
            raise HanabiRulesException(f'Invalid option {value} for rule {k}.')
        new_rule = HanabiRule(**(v._asdict() | {'value' : new_value}))
        setattr(self, k, new_rule)
        #reset rainbow_hint and rainbow_play if we've turned rainbows off
        if k == 'rainbow_enabled' and new_value == False:
            self.rainbow_hint = HanabiRule(
                **(self.rainbow_hint._asdict() | {'value' : self.DEFAULT_RAINBOW_HINT})
            )
            self.rainbow_play = HanabiRule(
                **(self.rainbow_play._asdict() | {'value' :self.DEFAULT_RAINBOW_PLAY})
            )

    def get_description(self, key):
        _, v = self._get_rule(key)
        return v.description

    def _get_rule(self, key):
        try:
            return key, vars(self)[key]
        except:
            candidates = [(k, v) for k, v in vars(self).items() if isinstance(v, HanabiRule) \
                                                              and v.short_form == key]
            if not candidates: raise KeyError(f'{key}: no such rule found.')
            if len(candidates) > 1: raise Exception('Two rules share a short form.')
            return candidates.pop()
       
    def __getitem__(self, key):
        _, v = self._get_rule(key)
        return v.value

    def __str__(self):
        header = ['rule', 'short form', 'current value', 'possible values']
        rows = [
            ['rainbow_enabled', self.rainbow_enabled.short_form,
                 self.rainbow_enabled.value, self.RAINBOW_ENABLED_OPTIONS],
            ['rainbow_hint', self.rainbow_hint.short_form,
                 self.rainbow_hint.value, str(self.RAINBOW_HINT_OPTIONS).replace("'", "")],
            ['rainbow_play', self.rainbow_play.short_form,
                 self.rainbow_play.value, str(self.RAINBOW_PLAY_OPTIONS).replace("'", "")],
            ['bombs_give_hints', self.bombs_give_hints.short_form,
                 self.bombs_give_hints.value, self.BOMBS_GIVE_HINTS_OPTIONS],
            ['extra_cards', self.extra_cards.short_form, self.extra_cards.value,
                f'[{self.EXTRA_CARDS_OPTIONS.start}, {self.EXTRA_CARDS_OPTIONS.stop - 1}]'],
            ['extra_hints', self.extra_hints.short_form, self.extra_hints.value, 
                f'[{self.EXTRA_HINTS_OPTIONS.start}, {self.EXTRA_HINTS_OPTIONS.stop - 1}]'],
            ['game_end', self.game_end.short_form,
                 self.game_end.value, str(self.GAME_END_OPTIONS).replace("'", "")]
        ]
        #omit how rainbow cards are treated if they do not exist
        if not self['rainbow_enabled']:
            del rows[2]
            del rows[1]
        return tabulate(rows, headers=header, tablefmt='pretty')


