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


class LadyCard(Card):
    __nickname__ = 'lady'


class CardSet:
    def __init__(self):
        self._cards = []

    def pick_card(self, other_set, other_card=None):
        if other_card is None:
            other_card = other_set._cards[random.randint(0, len(other_set)-1)]
        elif isinstance(other_card, str):
            other_card = [c for c in other_set._cards if c.__nickname__ == other_card][0]
        i = other_set._cards.index(other_card)
        self._cards.append(other_set._cards[i])
        other_set._cards.remove(other_card)

    def shuffle(self):
        random.shuffle(self._cards)

    def __str__(self):
        return 'middle'

    def __len__(self):
        return len(self._cards)

    def clone(self):
        cs = self.__class__()
        cs._cards = [c.clone() for c in self._cards]
        return cs


class MiddleCardSet(CardSet):
    def __init__(self):
        super().__init__()
        self._cards = [card() for card in (
            DuchessCard, AmbassadorCard, MurdererCard, CaptainCard, LadyCard,
        ) for _ in range(3)]
        self.shuffle()
