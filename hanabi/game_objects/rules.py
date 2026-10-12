from collections import namedtuple
from tabulate import tabulate
from hanabi.game_objects.color import Color
from hanabi.game_objects.exceptions import HanabiInputException, HanabiRulesException

HanabiRule = namedtuple('HanabiRule', ['value', 'short_form', 'allowed_values', 'description'])

class HanabiRuleset:

    RULES = {
        'rainbow_enabled': dict(
            default=False,
            kind='bool',
            options={True, False},
            short='re',
            desc=f'Determines whether the game will be played with rainbow '
                 f'({Color.MULTICOLOR}) cards.\n'
                 f'If True, rainbow cards will be used.  If False, they will not.\n'
                 f'When True, enables the rules for handling rainbow cards.'
        ),
        'rainbow_hint': dict(
            default='suit',
            kind='enum',
            options={'wild', 'suit'},
            short='rh',
            desc=f'Determines whether rainbow ({Color.MULTICOLOR}) cards are wild when hinted.\n'
                 f'If "wild", rainbow cards will always be treated as matching\n'
                 f'the color of a hint, and the rainbow color cannot be hinted.\n'
                 f'If "suit", rainbow can be hinted and only matches hints of\n'
                 f'rainbow color.  Rule available only if rainbow_enabled is True.'
        ),
        'rainbow_play': dict(
            default='suit',
            kind='enum',
            options={'wild', 'suit'},
            short='rp',
            desc=f'Determines whether rainbow ({Color.MULTICOLOR}) '
                 f'cards play into a separate suit\n'
                 f'(when set to "suit") or whether they are wild when played\n'
                 f'(when set to "wild").  A "wild" rainbow card can add to any\n'
                 f'color\'s firework for which its number is valid when played,\n'
                 f'determined by the player playing the card.  A "suit" rainbow\n'
                 f'card plays into the rainbow suit.'
        ),
        'bombs_give_hints': dict(
            default=True, #contrary to actual rules, but this is more fun
            kind='bool',
            options={True, False},
            short='bgh',
            desc='Determines whether wrongly played cards (triggering a misfire)\n'
                 'give a hint.  If True, a misfired card will restore a hint if\n'
                 'hints are below maximum.  If False, this will not happen.'
        ),
        'extra_cards': dict(
            default=0,
            kind='int',
            options=range(-1, 2),
            short='ec',
            desc='Modifies the number of cards each player is dealt and holds.\n'
                 'Negative numbers reduce hand size.'
        ),
        'extra_hints': dict(
            default=0,
            kind='int',
            options=range(-8, 4),
            short='eh',
            desc=f'Modifies the number of hints the players start with.\n'
                 f'Negative numbers reduce the number of hints.  Notably,\n'
                 f'the maximum number of hints (8) is not affected.\n'
                 f'Starting hints in excess of maximum are not lost until used\n'
                 f'but cannot be replenished, since discarding is illegal if\n'
                 f'the number of hints would be brought above maximum.'
        ),
        'game_end': dict(
            default='until_done',
            kind='enum',
            options={'until_done', 'final_round'},
            short='ge',
            desc=f'Determines the nature of the end of the game.  If set to \n'
                 f'"until_done", the game continues until the players exhaust all misfires,\n'
                 f'discard an essential card, or complete all fireworks.  If set to \n'
                 f'"final_round", after the last card is drawn, one complete \n'
                 f'round is taken, ending with the player who drew the last card,\n'
                 f'at which point the game is over.'
        ),
    }

    BOOL_WORDS = {'true': True, 'false': False}

    def __init__(self, rainbow_enabled  = RULES['rainbow_enabled']['default'],
                       rainbow_hint     = RULES['rainbow_hint']['default'],
                       rainbow_play     = RULES['rainbow_play']['default'],
                       bombs_give_hints = RULES['bombs_give_hints']['default'],
                       extra_cards      = RULES['extra_cards']['default'],
                       extra_hints      = RULES['extra_hints']['default'],
                       game_end         = RULES['game_end']['default']):

        supplied = {
            'rainbow_enabled' : rainbow_enabled,
            'rainbow_hint'    : rainbow_hint,
            'rainbow_play'    : rainbow_play,
            'bombs_give_hints': bombs_give_hints,
            'extra_cards'     : extra_cards,
            'extra_hints'     : extra_hints,
            'game_end'        : game_end,
        }
        for name, spec in self.RULES.items():
            rule = HanabiRule(supplied[name], spec['short'], spec['options'], spec['desc'])
            if rule.value not in rule.allowed_values:
                raise ValueError(f'{name} must be one of {spec["options"]}.')
            setattr(self, name, rule)

    def change_rule(self, rule, value):
        """
        Change a user-chosen rule to the user-chosen value, or fail if the (rule, value)
        pair is not appropriate.  rule and value are user-input strings which must be
        converted to the appropriate format.
        """
        try: k, v = self._get_rule(rule)
        except KeyError: raise HanabiInputException(f'No such rule: "{rule}".')
        if k in ('rainbow_hint', 'rainbow_play') and not self['rainbow_enabled']:
            raise HanabiRulesException('No rainbows in this game to toggle the handling of.')
        spec = self.RULES[k]
        new_value = self._parse_value(k, spec, v.value, value)
        if new_value not in v.allowed_values:
            raise HanabiInputException(f'Invalid option {value} for rule {k}.')
        new_rule = v._replace(value=new_value)
        setattr(self, k, new_rule)
        #reset rainbow_hint and rainbow_play if we've turned rainbows off
        if k == 'rainbow_enabled' and new_value == False:
            rh_default = self.RULES['rainbow_hint']['default']
            rp_default = self.RULES['rainbow_play']['default']
            self.rainbow_hint = self.rainbow_hint._replace(value=rh_default)
            self.rainbow_play = self.rainbow_play._replace(value=rp_default)

    @classmethod
    def _parse_value(cls, k, spec, current, value):
        """
        Convert user input for rule k into a value, dispatching on spec['kind'].
        A None value toggles bool rules and two-value enum rules; all other rules
        require an explicit value.  Input parsing should prevent empty or
        non-string values from reaching here.
        """
        if value is None:
            if spec['kind'] == 'bool': return not current
            if spec['kind'] == 'int':
                raise HanabiInputException('You must input a value to give the rule.')
            options = spec['options']
            #only a two-value rule can be toggled by omitting the new value
            if len(options) == 2: return (options - {current}).pop()
            shown = ', '.join(sorted(str(o) for o in options))
            raise HanabiInputException(f'Specify a value for rule {k}; options: {shown}')
        #input parsing should prevent empty or non-string values from reaching here
        if not isinstance(value, str) or value == '':
            raise RuntimeError(f'Rule value for {k!r} must be a non-empty string, got {value!r}.')
        if spec['kind'] == 'int':
            try: return int(value)
            except ValueError: raise HanabiInputException(f'Invalid option {value} for rule {k}')
        if spec['kind'] == 'bool':
            for word, parsed in cls.BOOL_WORDS.items():
                if word.startswith(value.lower()): return parsed
            return value
        matches = [o for o in sorted(spec['options']) if o.startswith(value.lower())]
        return matches[0] if len(matches) == 1 else value

    def get_description(self, key):
        try: _, v = self._get_rule(key)
        except KeyError: raise HanabiInputException(f'No such rule: "{key}".')
        return v.description

    def _get_rule(self, key):
        try: return key, vars(self)[key]
        except KeyError:
            candidates = [(k, v) for k, v in vars(self).items() if isinstance(v, HanabiRule) \
                                                              and v.short_form == key]
            if not candidates: raise KeyError(f'{key}: no such rule found.')
            if len(candidates) > 1: raise RuntimeError('Two rules share a short form.')
            return candidates.pop()

    def __getitem__(self, key):
        _, v = self._get_rule(key)
        return v.value

    @staticmethod
    def _format_options(options):
        if isinstance(options, range): return f'[{options.start}, {options.stop - 1}]'
        return '{' + ', '.join(sorted(str(o) for o in options)) + '}'

    def __str__(self):
        header = ['rule', 'short form', 'current value', 'possible values']
        rows = []
        for name, spec in self.RULES.items():
            #omit how rainbow cards are treated if they do not exist
            if name in ('rainbow_hint', 'rainbow_play') and not self['rainbow_enabled']: continue
            rule = getattr(self, name)
            rows.append([name, rule.short_form, rule.value,
                         self._format_options(spec['options'])])
        return tabulate(rows, headers=header, tablefmt='pretty')
