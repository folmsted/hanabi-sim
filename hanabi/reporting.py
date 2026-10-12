from hanabi.game_objects.actions import HintAction, DiscardAction, PlayAction, MisfireAction
from hanabi.game_objects.color import Color
from hanabi.game_objects.exceptions import HanabiSimException


def _playdiscardmisfire_sort_key(md, field):
    if 'round'.startswith(field):  return md.round
    if 'player'.startswith(field): return md.player
    if 'card'.startswith(field):   return md.action.realized.identity
    raise HanabiSimException(f'Unrecognized options "{field}".')

def sort_stats_playdiscardmisfire(metadata, sort):
    if not sort: return metadata
    if len(sort) > 1: raise HanabiSimException(f'Unrecognized options "{" ".join(sort)}".')
    return sorted(metadata, key=lambda md: _playdiscardmisfire_sort_key(md, sort[0].lower()))

def _hint_sort_key(md, field):
    if 'round'.startswith(field):  return md.round
    if 'giver'.startswith(field):  return md.player
    if 'target'.startswith(field): return md.action.targetplayer_index
    if 'number'.startswith(field): return len(md.action.positions)
    if 'hint'.startswith(field):
        #number hints sort before color hints; colors are offset past the numbers
        hint = md.action.hint
        return hint if isinstance(hint, int) else hint.value + len(Color)
    raise HanabiSimException(f'Unrecognized options "{field}".')

def sort_stats_hints(metadata, sort):
    if not sort: return metadata
    if len(sort) > 1: raise HanabiSimException(f'Unrecognized options "{" ".join(sort)}".')
    return sorted(metadata, key=lambda md: _hint_sort_key(md, sort[0].lower()))

def _player_sort_key(md, field):
    if 'round'.startswith(field):  return md.round
    if 'action'.startswith(field):
        return isinstance(md.action, HintAction)    * 1 + \
               isinstance(md.action, PlayAction)    * 2 + \
               isinstance(md.action, DiscardAction) * 3 + \
               isinstance(md.action, MisfireAction) * 4
    raise HanabiSimException(f'Unrecognized options "{field}".')

def sort_stats_players(metadata, sort):
    if not sort: return metadata
    if len(sort) > 1: raise HanabiSimException(f'Unrecognized options "{" ".join(sort)}".')
    return sorted(metadata, key=lambda md: _player_sort_key(md, sort[0].lower()))

#Given a list of potentially repeating elemets, return a map for unique elements
#to the number of times the element appeared in the list
def unique_counts(l):
    return { label : len([*filter(lambda x: x == label, l)]) for label in dict.fromkeys(l) }
