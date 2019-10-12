import numpy as np
import random
from coup.card import *
from coup.action import *


class Player(CardSet):
    def __init__(self, nickname=None, game=None):
        super().__init__()
        self.nickname = nickname
        self._treasure = 2
        self.game = game

    def exchange_card(self, card):
        assert not card.dead
        self.game.middle.pick_card(self, card)
        self.pick_card(self.game.middle)

    @property
    def treasure(self):
        return self._treasure

    def pay(self, n):
        if not n:
            return
        assert self._treasure >= n
        self._treasure -= n

    def income(self, n):
        if not n:
            return
        self._treasure += n

    def has_card(self, C):
        return [c for c in self._cards if isinstance(c, C) and not c.dead]

    @property
    def alive(self):
        return any(not c.dead for c in self._cards)

    def __str__(self):
        return self.nickname

    def clone(self):
        p = super(Player, self).clone()
        p.nickname = self.nickname
        p._treasure = self._treasure
        return p

    def _possible_actions(self):
        other_players = [p for p in self.game.players if p.alive and p != self]
        actions = [A(self, other_player) for A in ACTIONS if not issubclass(A, BlockAction)
                                         for other_player in (other_players if issubclass(A, DirectAction) else [None])]
        actions = [a for a in actions if a.can()]
        return actions

    def act(self):
        raise NotImplementedError

    def block(self, action, other):
        raise NotImplementedError

    def accuse(self, action, other):
        raise NotImplementedError

    def learn_card(self, card, set):
        raise NotImplementedError

    def learn_action(self, action):
        raise NotImplementedError

    def choose_kill(self):
        raise NotImplementedError

    def choose_look(self):
        raise NotImplementedError

    def __eq__(self, other):
        return self.nickname == other.nickname


class TruePlayer(Player):
    def act(self):
        print('Your turn!')
        print('Your cards: %s' % ' '.join([c.__nickname__.title() for c in self._cards if not c.dead]))
        actions = self._possible_actions()
        print('Your possible actions:\n%s' % '\n'.join(' %d: %s' % (i, str(a)) for i, a in enumerate(actions)))
        return actions[int(input('Your choice? '))]

    def block(self, action, other):
        actions = [BA(self, action, other) for BA in ACTIONS if issubclass(BA, BlockAction)]
        actions = [ba for ba in actions if ba.can()]
        if not actions:
            return None
        actions = ['nothing'] + actions
        print('Your turn to block!')
        print('Your cards: %s' % ' '.join([c.__nickname__.title() for c in self._cards if not c.dead]))
        print('Your possible blocking actions:\n%s' % '\n'.join(' %d: %s' % (i, str(a)) for i, a in enumerate(actions)))
        return actions[int(input('Your choice? '))]

    def accuse(self, action, other):
        return input('Accuse lying? (y/n) ') in ('y', 'Y')

    def choose_kill(self):
        print('Your got killed!')
        cards = [c for c in self._cards if not c.dead]
        if len(cards) == 1:
            return cards[0]
        elif len(cards) == 0:
            return None
        print('Your cards:\n%s' % '\n'.join([' %d: %s' % (i, c.__nickname__.title()) for i, c in enumerate(self._cards)]))
        return cards[int(input('Your choice? '))]

    def learn_card(self, card, set):
        print('%s in %s' % (card, set))

    def learn_action(self, action):
        print(str(action))

    def choose_look(self):
        print('Your got looked!')
        cards = [c for c in self._cards if not c.dead]
        if len(cards) == 1:
            return cards[0]
        print('Your cards:\n%s' % '\n'.join([' %d: %s' % (i, c.__nickname__.title()) for i, c in enumerate(self._cards)]))
        return cards[int(input('Your choice? '))]


class DumbPlayer(Player):
    def __init__(self, nickname=None, game=None):
        super().__init__(nickname, game)
        self.p_lying = np.random.normal(.5, .2)
        self.p_accusing = np.random.normal(.5, .2)

    def choose_kill(self):
        self.shuffle()
        cards = [c for c in self._cards if not c.dead]
        return cards[0] if len(cards) else None

    def act(self):
        actions = self._possible_actions()
        actions = [a for a in actions if a.truly_can() or random.random() > self.p_lying / len(actions)]
        random.shuffle(actions)
        return actions[0]

    def accuse(self, action, other):
        return random.random() < self.p_accusing

    def block(self, action, other):
        actions = [BA(self, action, other) for BA in ACTIONS if issubclass(BA, BlockAction)]
        actions = [ba for ba in actions if ba.can()]
        actions = [ba for ba in actions if ba.truly_can() or random.random() > self.p_lying / len(actions)]
        random.shuffle(actions)
        return actions[0] if actions else None

    def learn_card(self, card, set):
        pass

    def choose_look(self):
        self.shuffle()
        return [c for c in self._cards if not c.dead]

    def __repr__(self):
        return '%s (%s)' % (
            self.__class__.__name__,
            ' '.join('%s=%s' % x for x in dict(
                nickname=self.nickname,
                lying=round(self.p_lying, 2),
                accusing=round(self.p_accusing, 2),
            ).items())
        )


class SmartPlayer(DumbPlayer):
    def __init__(self, nickname=None, game=None):
        super().__init__(nickname, game)
        self.simulations = SimulatedGame

    def learn_card(self, card, set):
        super().learn_card(card, set)
