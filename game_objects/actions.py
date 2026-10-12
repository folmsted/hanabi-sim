from game_objects.card import RealizedCard


class HintAction:

    def __init__(self, targetplayer_index, hint, positions, before_hand, after_hand):
        self.targetplayer_index = targetplayer_index
        self.hint = hint
        self.positions = positions
        self.before_hand = before_hand
        self.after_hand = after_hand


class DiscardAction:

    def __init__(self, realized):
        self.realized = realized


class PlayAction:

    def __init__(self, realized):
        self.realized = realized


class MisfireAction:

    def __init__(self, realized):
        self.realized = realized


