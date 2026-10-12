class HintAction:

    def __init__(self, targetplayer_index, hint, positions, before_hand, after_hand):
        self.targetplayer_index = targetplayer_index
        self.hint = hint
        self.positions = positions
        self.before_hand = before_hand
        self.after_hand = after_hand


class DiscardAction:

    def __init__(self, card, card_state_on_discard):
        self.card = card
        self.card_state_on_discard = card_state_on_discard


class PlayAction:

    def __init__(self, card, card_state_on_play):
        self.card = card
        self.card_state_on_play = card_state_on_play


class MisfireAction:

    def __init__(self, card, card_state_on_misfire):
        self.card = card
        self.card_state_on_misfire = card_state_on_misfire


