import random


class Card:
    __nickname__ = None

    def __init__(self, dead=False):
        self.dead = dead

    def __repr__(self):
        return self.__nickname__.title() if self.dead else 'Unknwon'

    def clone(self):
        return self.__class__(dead=self.dead)


class DuchessCard(Card):
    __nickname__ = 'duchess'


class AmbassadorCard(Card):
    __nickname__ = 'ambassador'


class InquisitorCard(AmbassadorCard):
    __nickname__ = 'inquisitor'


class MurdererCard(Card):
    __nickname__ = 'murderer'


class CaptainCard(Card):
    __nickname__ = 'captain'


class CountessCard(Card):
    __nickname__ = 'countess'


class CardSet:
    def __init__(self):
        self.cards = []

    def pick_card(self, other_set, other_card=None):
        if other_card is None:
            other_card = other_set.cards[random.randint(0, len(other_set)-1)]
        if not isinstance(other_card, str):
            other_card = other_card.__nickname__
        if isinstance(other_card, str):
            other_card = [c for c in other_set.cards if c.__nickname__ == other_card][0]
        self.cards.append(other_card)
        other_set.cards.remove(other_card)
        return other_card

    def shuffle(self):
        random.shuffle(self.cards)

    def __str__(self):
        return 'middle'

    def __len__(self):
        return len(self.cards)

    def clone(self):
        cs = self.__class__()
        cs.cards = [c.clone() for c in self.cards]
        return cs

    def has_card(self, C):
        if isinstance(C, list): C = C[0]
        if not isinstance(C, str): C = C.__nickname__
        return [c for c in self.cards if c.__nickname__ == C and not c.dead]


class MiddleCardSet(CardSet):
    def __init__(self):
        super().__init__()
        self.cards = [card() for card in (
            DuchessCard, AmbassadorCard, MurdererCard, CaptainCard, CountessCard,
        ) for _ in range(3)]
        self.shuffle()
